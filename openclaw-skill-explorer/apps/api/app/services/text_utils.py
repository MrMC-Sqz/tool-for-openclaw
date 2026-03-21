from __future__ import annotations

from app.models.skill import Skill


def safe_lower(text: str | None) -> str:
    return (text or "").strip().lower()


def compact_text(parts: list[str | None]) -> str:
    cleaned_parts = []
    for part in parts:
        if not part:
            continue
        trimmed = " ".join(part.split())
        if trimmed:
            cleaned_parts.append(trimmed)
    return "\n".join(cleaned_parts)


def maybe_truncate(text: str, max_len: int) -> str:
    if max_len <= 0 or len(text) <= max_len:
        return text
    return text[:max_len]


def build_skill_analysis_text(skill: Skill) -> str:
    tag_names = []
    if getattr(skill, "tags", None):
        tag_names = [tag.name for tag in skill.tags if getattr(tag, "name", None)]

    parts = [
        skill.name,
        skill.description,
        skill.category,
        skill.install_method,
        ", ".join(tag_names) if tag_names else None,
        skill.raw_readme,
    ]
    return compact_text(parts)

