from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.skill import Skill
from app.schemas.skill import SkillListItem, SkillListResponse

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
