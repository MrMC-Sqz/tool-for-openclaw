from __future__ import annotations

import re
from datetime import datetime

from sqlalchemy.orm import Session, selectinload

from app.models.skill import Skill

TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
STOPWORDS = {
    "a",
    "an",
    "and",
    "as",
    "at",
    "by",
    "for",
    "from",
    "in",
    "into",
    "is",
    "of",
    "on",
    "or",
    "the",
    "to",
    "with",
}


def _tokenize(value: str | None) -> set[str]:
    if not value:
        return set()
    tokens = TOKEN_PATTERN.findall(value.lower())
    return {token for token in tokens if token not in STOPWORDS and len(token) > 1}


def _latest_risk_level(skill: Skill) -> str | None:
    if not skill.risk_reports:
        return None
    latest = max(
        skill.risk_reports,
        key=lambda report: (report.scanned_at or datetime.min, report.id),
    )
    return latest.risk_level


def _shared_tags(skill_a: Skill, skill_b: Skill) -> set[str]:
    tags_a = {tag.name.lower() for tag in skill_a.tags if tag.name}
    tags_b = {tag.name.lower() for tag in skill_b.tags if tag.name}
    return tags_a.intersection(tags_b)


def compute_similarity(skill_a: Skill, skill_b: Skill) -> int:
    score = 0

    if skill_a.category and skill_b.category and skill_a.category.lower() == skill_b.category.lower():
        score += 5

    score += len(_shared_tags(skill_a, skill_b)) * 3

    keywords_a = _tokenize(f"{skill_a.name or ''} {skill_a.readme_summary or ''}")
    keywords_b = _tokenize(f"{skill_b.name or ''} {skill_b.readme_summary or ''}")
    score += len(keywords_a.intersection(keywords_b))

    # Optional star-range similarity.
    if skill_a.stars and skill_b.stars:
        if abs(skill_a.stars - skill_b.stars) <= max(10, int(skill_a.stars * 0.5)):
            score += 1

    # Optional risk-level similarity.
    risk_a = _latest_risk_level(skill_a)
    risk_b = _latest_risk_level(skill_b)
    if risk_a and risk_b and risk_a == risk_b:
        score += 1

    return score


def get_similar_skills(db: Session, skill: Skill, top_k: int = 5) -> list[Skill]:
    candidates = (
        db.query(Skill)
        .options(
            selectinload(Skill.tags),
            selectinload(Skill.risk_reports),
        )
        .filter(Skill.id != skill.id)
        .all()
    )

    scored_candidates: list[tuple[int, Skill]] = []
    for candidate in candidates:
        similarity = compute_similarity(skill, candidate)
        if similarity > 0:
            scored_candidates.append((similarity, candidate))

    scored_candidates.sort(
        key=lambda item: (
            -item[0],
            -(item[1].stars or 0),
            -(item[1].updated_at.timestamp() if item[1].updated_at else 0),
        )
    )
    return [skill for _, skill in scored_candidates[:top_k]]
