from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.skill import Skill
from app.schemas.risk import RiskReportOut
from app.schemas.skill import SkillDetailResponse, SkillListItem, SkillListResponse
from app.services.risk_service import (
    create_risk_report_for_skill,
    get_latest_risk_report_for_skill,
    risk_report_to_scan_result,
)

router = APIRouter(prefix="/api/skills", tags=["skills"])


@router.get("", response_model=SkillListResponse)
def list_skills(
    q: str | None = Query(default=None),
    category: str | None = Query(default=None),
    sort: str = Query(default="stars_desc"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> SkillListResponse:
    query = db.query(Skill)

    if q:
        like_query = f"%{q.strip()}%"
        query = query.filter(
            or_(
                Skill.name.ilike(like_query),
                Skill.description.ilike(like_query),
            )
        )

    if category:
        query = query.filter(Skill.category == category.strip())

    if sort == "updated_desc":
        query = query.order_by(Skill.last_repo_updated_at.is_(None), Skill.last_repo_updated_at.desc())
    elif sort == "name_asc":
        query = query.order_by(Skill.name.asc())
    else:
        query = query.order_by(Skill.stars.desc(), Skill.name.asc())

    total = query.count()
    offset = (page - 1) * page_size
    skills = query.offset(offset).limit(page_size).all()

    items = [
        SkillListItem(
            name=skill.name,
            slug=skill.slug,
            description=skill.description,
            category=skill.category,
            stars=skill.stars,
            last_repo_updated_at=skill.last_repo_updated_at,
        )
        for skill in skills
    ]
    return SkillListResponse(items=items, total=total, page=page, page_size=page_size)


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
    skill = db.query(Skill).filter(Skill.slug == slug).first()
    if not skill:
        raise HTTPException(status_code=404, detail="skill not found")

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
        latest_risk_report=_risk_report_out_or_none(latest_report),
    )


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
