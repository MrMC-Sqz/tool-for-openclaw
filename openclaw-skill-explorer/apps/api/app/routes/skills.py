from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.models.skill import Skill
from app.schemas.risk import RiskReportOut
from app.schemas.skill import SimilarSkillsResponse, SkillDetailResponse, SkillListItem, SkillListResponse
from app.services.recommendation_service import get_similar_skills
from app.services.risk_service import (
    create_risk_report_for_skill,
    get_latest_risk_report_for_skill,
    risk_report_to_scan_result,
)
from app.services.skill_service import ensure_skill_readme_summary, search_skills

router = APIRouter(prefix="/api/skills", tags=["skills"])


@router.get("", response_model=SkillListResponse)
def list_skills(
    q: str | None = Query(default=None),
    category: str | None = Query(default=None),
    risk_level: str | None = Query(default=None),
    min_stars: int | None = Query(default=None, ge=0),
    updated_after: datetime | None = Query(default=None),
    sort: str = Query(default="stars_desc"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> SkillListResponse:
    result = search_skills(
        db=db,
        query=q,
        filters={
            "category": category,
            "risk_level": risk_level,
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
        )
        for skill in skills
    ]
    return SkillListResponse(items=items, total=result["total"], page=page, page_size=page_size)


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

    try:
        ensure_skill_readme_summary(db, skill)
        db.commit()
        db.refresh(skill)
    except SQLAlchemyError:
        db.rollback()

    latest_report = get_latest_risk_report_for_skill(db, skill.id)
    return SkillDetailResponse(
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
    )


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
def rescan_skill(slug: str, db: Session = Depends(get_db)) -> RiskReportOut:
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
    return RiskReportOut(
        id=report.id,
        skill_id=report.skill_id,
        input_type=report.input_type,
        scanned_at=report.scanned_at,
        **payload,
    )
