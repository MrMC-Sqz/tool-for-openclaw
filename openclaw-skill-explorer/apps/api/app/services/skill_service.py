from __future__ import annotations

from datetime import datetime

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.skill import Skill
from app.models.source import Source


def get_or_create_curated_source(db: Session) -> Source:
    source = db.query(Source).filter(Source.name == "OpenClaw Curated Seed").first()
    if source:
        return source

    source = Source(
        name="OpenClaw Curated Seed",
        type="curated_list",
        base_url="local://scripts/data/skills_seed.json",
        is_active=1,
        sync_status="idle",
    )
    db.add(source)
    db.flush()
    return source


def upsert_skill(db: Session, normalized_data: dict, source_id: int | None = None) -> tuple[Skill, str]:
    filters = [Skill.slug == normalized_data["slug"]]
    repo_url = normalized_data.get("repo_url")
    if repo_url:
        filters.append(Skill.repo_url == repo_url)

    skill = db.query(Skill).filter(or_(*filters)).first()
    action = "updated"
    if not skill:
        skill = Skill(slug=normalized_data["slug"])
        db.add(skill)
        action = "inserted"

    for field, value in normalized_data.items():
        setattr(skill, field, value)

    if source_id is not None:
        skill.source_id = source_id
    skill.updated_at = datetime.utcnow()
    db.flush()
    return skill, action

