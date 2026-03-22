from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from app.core.config import settings
from app.core.security import require_roles
from app.db.session import get_db
from app.models.skill import Skill
from app.models.skill_review import SkillReview
from app.schemas.job import ScanJobCreateResponse
from app.schemas.risk import RiskReportOut
from app.schemas.skill import (
    ReviewSummaryItemOut,
    ReviewSummaryResponse,
    RemediationChecklistResponse,
    ScanDeltaResponse,
    SkillAuditLogListResponse,
    SkillAuditLogOut,
    SimilarSkillsResponse,
    SkillDetailResponse,
    SkillListItem,
    SkillListResponse,
    SkillReviewCreateRequest,
    SkillReviewListResponse,
    SkillReviewOut,
)
from app.services.job_service import create_scan_job, enqueue_scan_job
from app.services.recommendation_service import get_similar_skills
from app.services.review_service import (
    build_remediation_checklist,
    create_skill_review,
    get_skill_review_state,
    list_skill_audit_logs,
    list_skill_reviews,
)
from app.services.risk_service import (
    compute_scan_delta,
    create_risk_report_for_skill,
    get_latest_risk_report_for_skill,
    list_recent_risk_reports_for_skill,
    risk_report_to_scan_result,
)
from app.services.skill_service import ensure_skill_readme_summary, search_skills
from app.services.cache_service import get_cache, invalidate_prefix, make_cache_key, set_cache

router = APIRouter(
    prefix="/api/skills",
    tags=["skills"],
    dependencies=[Depends(require_roles("viewer", "reviewer", "admin"))],
)
SKILLS_LIST_CACHE_PREFIX = "skills:list"
SKILL_DETAIL_CACHE_PREFIX = "skills:detail"


def _invalidate_skills_cache(slug: str | None = None) -> None:
    invalidate_prefix(f"{SKILLS_LIST_CACHE_PREFIX}:")
    if slug:
        invalidate_prefix(f"{SKILL_DETAIL_CACHE_PREFIX}:{slug}:")
    else:
        invalidate_prefix(f"{SKILL_DETAIL_CACHE_PREFIX}:")


@router.get("", response_model=SkillListResponse)
def list_skills(
    q: str | None = Query(default=None),
    category: str | None = Query(default=None),
    risk_level: str | None = Query(default=None),
    review_state: str | None = Query(default=None),
    reviewer: str | None = Query(default=None),
    min_stars: int | None = Query(default=None, ge=0),
    updated_after: datetime | None = Query(default=None),
    sort: str = Query(default="stars_desc"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> SkillListResponse:
    cache_key = make_cache_key(
        SKILLS_LIST_CACHE_PREFIX,
        {
            "q": q,
            "category": category,
            "risk_level": risk_level,
            "review_state": review_state,
            "reviewer": reviewer,
            "min_stars": min_stars,
            "updated_after": updated_after.isoformat() if updated_after else None,
            "sort": sort,
            "page": page,
            "page_size": page_size,
        },
    )
    if settings.cache_enabled:
        cached = get_cache(cache_key)
        if cached is not None:
            return cached

    result = search_skills(
        db=db,
        query=q,
        filters={
            "category": category,
            "risk_level": risk_level,
            "review_state": review_state,
            "reviewer": reviewer,
            "min_stars": min_stars,
            "updated_after": updated_after,
        },
        pagination={
            "sort": sort,
            "page": page,
            "page_size": page_size,
        },
    )
    skills = result["items"]
    latest_reports = result["latest_reports"]
    review_states = result["review_states"]
    latest_reviewers = result["latest_reviewers"]
    relevance_scores = result["relevance_scores"]

    items = [
        SkillListItem(
            name=skill.name,
            slug=skill.slug,
            description=skill.description,
            category=skill.category,
            stars=skill.stars,
            last_repo_updated_at=skill.last_repo_updated_at,
            risk_level=latest_reports.get(skill.id).risk_level if latest_reports.get(skill.id) else None,
            relevance_score=relevance_scores.get(skill.id),
            review_state=review_states.get(skill.id, "pending_review"),
            latest_reviewer=latest_reviewers.get(skill.id),
        )
        for skill in skills
    ]
    response = SkillListResponse(items=items, total=result["total"], page=page, page_size=page_size)
    if settings.cache_enabled:
        set_cache(cache_key, response, settings.cache_ttl_seconds)
    return response


@router.get("/reviews/summary", response_model=ReviewSummaryResponse)
def get_review_summary(
    reviewer: str | None = Query(default=None),
    decision: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
) -> ReviewSummaryResponse:
    query = db.query(SkillReview, Skill.slug).join(Skill, Skill.id == SkillReview.skill_id)

    if reviewer:
        query = query.filter(SkillReview.reviewer == reviewer.strip())
    if decision:
        query = query.filter(SkillReview.decision == decision.strip().lower())

    rows = query.order_by(SkillReview.created_at.desc(), SkillReview.id.desc()).limit(limit).all()

    by_decision: dict[str, int] = {}
    by_reviewer: dict[str, int] = {}
    recent_items: list[ReviewSummaryItemOut] = []

    for review, skill_slug in rows:
        by_decision[review.decision] = by_decision.get(review.decision, 0) + 1
        by_reviewer[review.reviewer] = by_reviewer.get(review.reviewer, 0) + 1
        recent_items.append(
            ReviewSummaryItemOut(
                review_id=review.id,
                skill_slug=skill_slug,
                reviewer=review.reviewer,
                decision=review.decision,
                created_at=review.created_at,
            )
        )

    return ReviewSummaryResponse(
        total_reviews=len(rows),
        by_decision=by_decision,
        by_reviewer=by_reviewer,
        recent_items=recent_items,
    )


@router.get("/reviews/export")
def export_review_summary_csv(
    reviewer: str | None = Query(default=None),
    decision: str | None = Query(default=None),
    limit: int = Query(default=1000, ge=1, le=5000),
    db: Session = Depends(get_db),
) -> Response:
    query = db.query(SkillReview, Skill.slug).join(Skill, Skill.id == SkillReview.skill_id)
    if reviewer:
        query = query.filter(SkillReview.reviewer == reviewer.strip())
    if decision:
        query = query.filter(SkillReview.decision == decision.strip().lower())

    rows = query.order_by(SkillReview.created_at.desc(), SkillReview.id.desc()).limit(limit).all()
    lines = ["review_id,skill_slug,reviewer,decision,comment,override_reason,created_at"]
    for review, skill_slug in rows:
        comment = (review.comment or "").replace('"', '""')
        override_reason = (review.override_reason or "").replace('"', '""')
        lines.append(
            f'{review.id},{skill_slug},{review.reviewer},{review.decision},"{comment}","{override_reason}",{review.created_at.isoformat()}'
        )
    csv_text = "\n".join(lines)
    headers = {"Content-Disposition": 'attachment; filename="skill_review_summary.csv"'}
    return Response(content=csv_text, media_type="text/csv", headers=headers)


def _risk_report_out_or_none(report) -> RiskReportOut | None:
    if report is None:
        return None
    payload = risk_report_to_scan_result(report)
    return RiskReportOut(
        id=report.id,
        skill_id=report.skill_id,
        input_type=report.input_type,
        scanned_at=report.scanned_at,
        **payload,
    )


@router.get("/{slug}", response_model=SkillDetailResponse)
def get_skill_detail(slug: str, db: Session = Depends(get_db)) -> SkillDetailResponse:
    cache_key = make_cache_key(f"{SKILL_DETAIL_CACHE_PREFIX}:{slug}", {"slug": slug})
    if settings.cache_enabled:
        cached = get_cache(cache_key)
        if cached is not None:
            return cached

    skill = (
        db.query(Skill)
        .options(
            selectinload(Skill.tags),
            selectinload(Skill.risk_reports),
            selectinload(Skill.reviews),
        )
        .filter(Skill.slug == slug)
        .first()
    )
    if not skill:
        raise HTTPException(status_code=404, detail="skill not found")

    try:
        ensure_skill_readme_summary(db, skill)
        db.commit()
        db.refresh(skill)
    except SQLAlchemyError:
        db.rollback()

    latest_report = get_latest_risk_report_for_skill(db, skill.id)
    response = SkillDetailResponse(
        name=skill.name,
        slug=skill.slug,
        repo_url=skill.repo_url,
        repo_owner=skill.repo_owner,
        repo_name=skill.repo_name,
        description=skill.description,
        category=skill.category,
        stars=skill.stars,
        last_repo_updated_at=skill.last_repo_updated_at,
        readme_summary=skill.readme_summary,
        latest_risk_report=_risk_report_out_or_none(latest_report),
        review_state=get_skill_review_state(skill),
    )
    if settings.cache_enabled:
        set_cache(cache_key, response, settings.cache_ttl_seconds)
    return response


@router.get("/{slug}/similar", response_model=SimilarSkillsResponse)
def get_skill_similar(
    slug: str,
    top_k: int = Query(default=5, ge=1, le=20),
    db: Session = Depends(get_db),
) -> SimilarSkillsResponse:
    skill = (
        db.query(Skill)
        .options(
            selectinload(Skill.tags),
            selectinload(Skill.risk_reports),
        )
        .filter(Skill.slug == slug)
        .first()
    )
    if not skill:
        raise HTTPException(status_code=404, detail="skill not found")

    similar_skills = get_similar_skills(db, skill, top_k=top_k)
    items = [
        SkillListItem(
            name=item.name,
            slug=item.slug,
            description=item.description,
            category=item.category,
            stars=item.stars,
            last_repo_updated_at=item.last_repo_updated_at,
            risk_level=(
                max(
                    item.risk_reports,
                    key=lambda report: (report.scanned_at or datetime.min, report.id),
                ).risk_level
                if item.risk_reports
                else None
            ),
            relevance_score=None,
        )
        for item in similar_skills
    ]
    return SimilarSkillsResponse(items=items)


@router.post("/{slug}/scan", response_model=RiskReportOut)
def rescan_skill(
    slug: str,
    _role: str = Depends(require_roles("reviewer", "admin")),
    db: Session = Depends(get_db),
) -> RiskReportOut:
    skill = db.query(Skill).filter(Skill.slug == slug).first()
    if not skill:
        raise HTTPException(status_code=404, detail="skill not found")

    try:
        report, _ = create_risk_report_for_skill(db, skill)
        db.commit()
        db.refresh(report)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="failed to persist risk report")

    payload = risk_report_to_scan_result(report)
    response = RiskReportOut(
        id=report.id,
        skill_id=report.skill_id,
        input_type=report.input_type,
        scanned_at=report.scanned_at,
        **payload,
    )
    _invalidate_skills_cache(slug)
    return response


@router.post("/{slug}/scan/jobs", response_model=ScanJobCreateResponse)
def submit_skill_scan_job(
    slug: str,
    _role: str = Depends(require_roles("reviewer", "admin")),
    db: Session = Depends(get_db),
) -> ScanJobCreateResponse:
    skill = db.query(Skill).filter(Skill.slug == slug).first()
    if not skill:
        raise HTTPException(status_code=404, detail="skill not found")

    try:
        job = create_scan_job(db, input_type="skill", skill_id=skill.id)
        db.commit()
        db.refresh(job)
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc))
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="failed to create skill scan job")

    enqueue_scan_job(job.id)
    return ScanJobCreateResponse(job_id=job.id, status=job.status)


@router.get("/{slug}/reviews", response_model=SkillReviewListResponse)
def get_skill_reviews(slug: str, db: Session = Depends(get_db)) -> SkillReviewListResponse:
    skill = db.query(Skill).filter(Skill.slug == slug).first()
    if not skill:
        raise HTTPException(status_code=404, detail="skill not found")

    reviews = list_skill_reviews(db, skill.id)
    return SkillReviewListResponse(
        items=[
            SkillReviewOut(
                id=review.id,
                reviewer=review.reviewer,
                decision=review.decision,
                comment=review.comment,
                override_reason=review.override_reason,
                created_at=review.created_at,
            )
            for review in reviews
        ]
    )


@router.post("/{slug}/reviews", response_model=SkillReviewOut)
def submit_skill_review(
    slug: str,
    payload: SkillReviewCreateRequest,
    _role: str = Depends(require_roles("reviewer", "admin")),
    db: Session = Depends(get_db),
) -> SkillReviewOut:
    skill = db.query(Skill).filter(Skill.slug == slug).first()
    if not skill:
        raise HTTPException(status_code=404, detail="skill not found")

    try:
        review = create_skill_review(
            db,
            skill=skill,
            reviewer=payload.reviewer,
            decision=payload.decision,
            comment=payload.comment,
            override_reason=payload.override_reason,
        )
        db.commit()
        db.refresh(review)
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc))
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="failed to persist review decision")

    _invalidate_skills_cache(slug)
    return SkillReviewOut(
        id=review.id,
        reviewer=review.reviewer,
        decision=review.decision,
        comment=review.comment,
        override_reason=review.override_reason,
        created_at=review.created_at,
    )


@router.get("/{slug}/audit-logs", response_model=SkillAuditLogListResponse)
def get_skill_audit_logs(slug: str, db: Session = Depends(get_db)) -> SkillAuditLogListResponse:
    skill = db.query(Skill).filter(Skill.slug == slug).first()
    if not skill:
        raise HTTPException(status_code=404, detail="skill not found")

    logs = list_skill_audit_logs(db, skill.id)
    return SkillAuditLogListResponse(
        items=[
            SkillAuditLogOut(
                id=item.id,
                action_type=item.action_type,
                actor=item.actor,
                payload_json=item.payload_json,
                created_at=item.created_at,
            )
            for item in logs
        ]
    )


@router.get("/{slug}/remediation-checklist", response_model=RemediationChecklistResponse)
def get_skill_remediation_checklist(
    slug: str,
    db: Session = Depends(get_db),
) -> RemediationChecklistResponse:
    skill = (
        db.query(Skill)
        .options(
            selectinload(Skill.reviews),
            selectinload(Skill.risk_reports),
        )
        .filter(Skill.slug == slug)
        .first()
    )
    if not skill:
        raise HTTPException(status_code=404, detail="skill not found")

    latest_report = get_latest_risk_report_for_skill(db, skill.id)
    if not latest_report:
        return RemediationChecklistResponse(
            review_state=get_skill_review_state(skill),
            risk_level=None,
            items=[],
        )

    result = risk_report_to_scan_result(latest_report)
    checklist = build_remediation_checklist(result["flags"])
    return RemediationChecklistResponse(
        review_state=get_skill_review_state(skill),
        risk_level=result["risk_level"],
        items=checklist,
    )


@router.get("/{slug}/scan-delta", response_model=ScanDeltaResponse)
def get_skill_scan_delta(
    slug: str,
    db: Session = Depends(get_db),
) -> ScanDeltaResponse:
    skill = db.query(Skill).filter(Skill.slug == slug).first()
    if not skill:
        raise HTTPException(status_code=404, detail="skill not found")

    reports = list_recent_risk_reports_for_skill(db, skill.id, limit=2)
    if len(reports) < 2:
        raise HTTPException(status_code=400, detail="at least two risk reports are required")

    current_report, previous_report = reports[0], reports[1]
    delta = compute_scan_delta(previous_report=previous_report, current_report=current_report)
    return ScanDeltaResponse(**delta)
