from __future__ import annotations

from datetime import datetime
from typing import TypedDict

from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload

from app.models.risk_report import RiskReport
from app.models.skill import Skill
from app.models.source import Source
from app.services.review_service import get_latest_skill_review, get_skill_review_state
from app.services.summarizer import summarize_readme

SEARCH_WEIGHTS = {
    "name": 5,
    "description": 3,
    "readme_summary": 2,
    "category": 2,
    "tags": 2,
}


class SearchSkillsResult(TypedDict):
    items: list[Skill]
    total: int
    relevance_scores: dict[int, int]
    latest_reports: dict[int, RiskReport | None]
    review_states: dict[int, str]
    latest_reviewers: dict[int, str | None]


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


def ensure_skill_readme_summary(db: Session, skill: Skill) -> str | None:
    if skill.readme_summary and skill.readme_summary.strip():
        return skill.readme_summary

    source_text = (skill.raw_readme or "").strip()
    if not source_text:
        fallback = (skill.description or "").strip() or (skill.normalized_text or "").strip()
        if fallback:
            source_text = fallback
        else:
            return None

    summary = summarize_readme(source_text)
    if not summary:
        return None

    skill.readme_summary = summary
    db.add(skill)
    db.flush()
    return summary


def _latest_risk_report(skill: Skill) -> RiskReport | None:
    if not skill.risk_reports:
        return None
    return max(
        skill.risk_reports,
        key=lambda report: (report.scanned_at or datetime.min, report.id),
    )


def _contains(haystack: str | None, needle: str) -> bool:
    if not haystack:
        return False
    return needle in haystack.lower()


def _compute_relevance_score(skill: Skill, query: str) -> int:
    score = 0
    if _contains(skill.name, query):
        score += SEARCH_WEIGHTS["name"]
    if _contains(skill.description, query):
        score += SEARCH_WEIGHTS["description"]
    if _contains(skill.readme_summary, query):
        score += SEARCH_WEIGHTS["readme_summary"]
    if _contains(skill.category, query):
        score += SEARCH_WEIGHTS["category"]
    if any(_contains(tag.name, query) for tag in skill.tags):
        score += SEARCH_WEIGHTS["tags"]
    return score


def search_skills(
    db: Session,
    query: str | None,
    filters: dict,
    pagination: dict,
) -> SearchSkillsResult:
    normalized_query = (query or "").strip().lower()
    normalized_category = (filters.get("category") or "").strip()
    normalized_risk_level = (filters.get("risk_level") or "").strip().upper()
    normalized_review_state = (filters.get("review_state") or "").strip().lower()
    normalized_reviewer = (filters.get("reviewer") or "").strip().lower()
    min_stars = filters.get("min_stars")
    updated_after = filters.get("updated_after")
    sort = pagination.get("sort", "stars_desc")
    page = max(1, int(pagination.get("page", 1)))
    page_size = max(1, int(pagination.get("page_size", 20)))

    db_query = (
        db.query(Skill)
        .options(
            selectinload(Skill.tags),
            selectinload(Skill.risk_reports),
            selectinload(Skill.reviews),
        )
    )
    if normalized_category:
        db_query = db_query.filter(Skill.category == normalized_category)
    if min_stars is not None:
        db_query = db_query.filter(Skill.stars >= int(min_stars))
    if updated_after is not None:
        db_query = db_query.filter(Skill.last_repo_updated_at >= updated_after)

    candidates = db_query.all()

    latest_reports: dict[int, RiskReport | None] = {
        skill.id: _latest_risk_report(skill) for skill in candidates
    }
    review_states: dict[int, str] = {skill.id: get_skill_review_state(skill) for skill in candidates}
    latest_reviewers: dict[int, str | None] = {
        skill.id: (
            (latest_review.reviewer.strip() if latest_review and latest_review.reviewer else None)
        )
        for skill in candidates
        for latest_review in [get_latest_skill_review(skill)]
    }
    if normalized_risk_level:
        candidates = [
            skill
            for skill in candidates
            if latest_reports.get(skill.id)
            and latest_reports[skill.id].risk_level.upper() == normalized_risk_level
        ]
    if normalized_review_state:
        candidates = [
            skill
            for skill in candidates
            if review_states.get(skill.id, "pending_review") == normalized_review_state
        ]
    if normalized_reviewer:
        candidates = [
            skill
            for skill in candidates
            if (latest_reviewers.get(skill.id) or "").lower() == normalized_reviewer
        ]

    relevance_scores: dict[int, int] = {}
    if normalized_query:
        matched: list[Skill] = []
        for skill in candidates:
            score = _compute_relevance_score(skill, normalized_query)
            if score > 0:
                relevance_scores[skill.id] = score
                matched.append(skill)
        candidates = matched
    else:
        relevance_scores = {skill.id: 0 for skill in candidates}

    if normalized_query:
        candidates.sort(
            key=lambda skill: (
                -relevance_scores.get(skill.id, 0),
                -(skill.stars or 0),
                -(skill.updated_at.timestamp() if skill.updated_at else 0),
            )
        )
    elif sort == "updated_desc":
        candidates.sort(
            key=lambda skill: (
                -(skill.last_repo_updated_at.timestamp() if skill.last_repo_updated_at else 0),
                -(skill.stars or 0),
                skill.name.lower(),
            )
        )
    elif sort == "name_asc":
        candidates.sort(
            key=lambda skill: (
                skill.name.lower(),
                -(skill.stars or 0),
            )
        )
    else:
        candidates.sort(
            key=lambda skill: (
                -(skill.stars or 0),
                -(skill.last_repo_updated_at.timestamp() if skill.last_repo_updated_at else 0),
                skill.name.lower(),
            )
        )

    total = len(candidates)
    offset = (page - 1) * page_size
    items = candidates[offset : offset + page_size]
    return {
        "items": items,
        "total": total,
        "relevance_scores": relevance_scores,
        "latest_reports": latest_reports,
        "review_states": review_states,
        "latest_reviewers": latest_reviewers,
    }
