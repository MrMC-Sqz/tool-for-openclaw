from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.security import require_roles
from app.db.session import get_db
from app.models.source import Source
from app.models.skill import Skill
from app.schemas.source import SourceListItem, SourceListResponse

router = APIRouter(
    prefix="/api/sources",
    tags=["sources"],
    dependencies=[Depends(require_roles("viewer", "reviewer", "admin"))],
)


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
