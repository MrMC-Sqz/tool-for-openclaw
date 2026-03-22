from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from app.core.security import require_roles
from app.db.session import get_db
from app.models.source import Source
from app.models.skill import Skill
from app.schemas.job import ScanJobCreateResponse
from app.schemas.skill import SkillListItem
from app.schemas.source import SourceDetailResponse, SourceListItem, SourceListResponse
from app.services.job_service import create_scan_job, enqueue_scan_job
from app.services.review_service import get_skill_review_state

router = APIRouter(
    prefix="/api/sources",
    tags=["sources"],
    dependencies=[Depends(require_roles("viewer", "reviewer", "admin"))],
)


def _latest_risk_level(skill: Skill) -> str | None:
    if not skill.risk_reports:
        return None
    latest_report = max(
        skill.risk_reports,
        key=lambda report: (report.scanned_at or datetime.min, report.id),
    )
    return latest_report.risk_level


@router.get("", response_model=SourceListResponse)
def list_sources(db: Session = Depends(get_db)) -> SourceListResponse:
    rows = (
        db.query(Source, func.count(Skill.id))
        .outerjoin(Skill, Skill.source_id == Source.id)
        .group_by(Source.id)
        .order_by(func.count(Skill.id).desc(), Source.last_synced_at.desc(), Source.name.asc())
        .all()
    )
    return SourceListResponse(
        items=[
            SourceListItem(
                id=source.id,
                name=source.name,
                type=source.type,
                base_url=source.base_url,
                is_active=source.is_active,
                sync_status=source.sync_status,
                last_synced_at=source.last_synced_at,
                updated_at=source.updated_at,
                skill_count=int(skill_count or 0),
            )
            for source, skill_count in rows
        ]
    )


@router.get("/{source_id}", response_model=SourceDetailResponse)
def get_source_detail(source_id: int, db: Session = Depends(get_db)) -> SourceDetailResponse:
    source = (
        db.query(Source)
        .options(
            selectinload(Source.skills).selectinload(Skill.risk_reports),
            selectinload(Source.skills).selectinload(Skill.reviews),
        )
        .filter(Source.id == source_id)
        .first()
    )
    if not source:
        raise HTTPException(status_code=404, detail="source not found")

    skills = sorted(
        source.skills,
        key=lambda skill: (
            -(skill.stars or 0),
            -(skill.last_repo_updated_at.timestamp() if skill.last_repo_updated_at else 0),
            skill.name.lower(),
        ),
    )

    categories: dict[str, int] = {}
    risk_levels: dict[str, int] = {}
    for skill in skills:
        category = (skill.category or "uncategorized").strip().lower()
        categories[category] = categories.get(category, 0) + 1

        risk_level = (_latest_risk_level(skill) or "unknown").strip().upper()
        risk_levels[risk_level] = risk_levels.get(risk_level, 0) + 1

    return SourceDetailResponse(
        id=source.id,
        name=source.name,
        type=source.type,
        base_url=source.base_url,
        is_active=source.is_active,
        sync_status=source.sync_status,
        last_synced_at=source.last_synced_at,
        updated_at=source.updated_at,
        skill_count=len(skills),
        categories=dict(sorted(categories.items(), key=lambda item: (-item[1], item[0]))),
        risk_levels=dict(sorted(risk_levels.items(), key=lambda item: (-item[1], item[0]))),
        skills=[
            SkillListItem(
                name=skill.name,
                slug=skill.slug,
                description=skill.description,
                category=skill.category,
                stars=skill.stars,
                last_repo_updated_at=skill.last_repo_updated_at,
                risk_level=_latest_risk_level(skill),
                relevance_score=None,
                review_state=get_skill_review_state(skill),
                latest_reviewer=None,
            )
            for skill in skills[:40]
        ],
    )


@router.post("/{source_id}/sync/jobs", response_model=ScanJobCreateResponse)
def submit_source_sync_job(
    source_id: int,
    _role: str = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
) -> ScanJobCreateResponse:
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="source not found")

    try:
        job = create_scan_job(db, input_type="sync_source", input_value=source.name)
        db.commit()
        db.refresh(job)
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc))
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="failed to create source sync job")

    enqueue_scan_job(job.id)
    return ScanJobCreateResponse(job_id=job.id, status=job.status)
