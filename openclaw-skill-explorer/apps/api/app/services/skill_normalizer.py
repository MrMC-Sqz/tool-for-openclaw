from __future__ import annotations

import re
from datetime import datetime

from app.services.github_service import RepoMetadata, extract_owner_repo

SLUG_INVALID_PATTERN = re.compile(r"[^a-z0-9-]+")
SLUG_HYPHEN_PATTERN = re.compile(r"-{2,}")


def generate_slug(name: str) -> str:
    slug = name.strip().lower().replace(" ", "-")
    slug = SLUG_INVALID_PATTERN.sub("", slug)
    slug = SLUG_HYPHEN_PATTERN.sub("-", slug).strip("-")
    return slug or "unnamed-skill"


def _parse_datetime(datetime_value: str | None) -> datetime | None:
    if not datetime_value:
        return None
    try:
        return datetime.fromisoformat(datetime_value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _parse_tags(raw_tags) -> list[str]:
    if not isinstance(raw_tags, list):
        return []

    normalized_tags: list[str] = []
    seen: set[str] = set()
    for raw_tag in raw_tags:
        tag = str(raw_tag or "").strip().lower()
        if not tag or tag in seen:
            continue
        seen.add(tag)
        normalized_tags.append(tag)
    return normalized_tags


def normalize_skill_data(
    seed_item: dict,
    github_metadata: RepoMetadata,
    readme_text: str,
) -> dict:
    seed_name = str(seed_item.get("name") or "").strip()
    repo_url = str(seed_item.get("repo_url") or "").strip() or None
    source_url = str(seed_item.get("source_url") or "").strip() or None
    seed_description = str(seed_item.get("description") or "").strip() or None
    category = str(seed_item.get("category") or "").strip() or None
    author = str(seed_item.get("author") or "").strip() or None
    install_method = str(seed_item.get("install_method") or "").strip() or None
    seed_summary = str(seed_item.get("readme_summary") or "").strip() or None
    raw_manifest = str(seed_item.get("raw_manifest") or "").strip() or None
    seed_readme = str(seed_item.get("raw_readme") or "").strip()
    seed_tags = _parse_tags(seed_item.get("tags"))
    seed_stars = int(seed_item.get("stars") or 0)
    seed_updated_at = _parse_datetime(seed_item.get("last_repo_updated_at"))

    owner_from_url, repo_from_url = extract_owner_repo(repo_url)
    repo_owner = github_metadata.repo_owner or owner_from_url
    repo_name = github_metadata.repo_name or repo_from_url

    final_name = (github_metadata.name or seed_name or repo_name or "Unnamed Skill").strip()
    final_description = (github_metadata.description or seed_description or "").strip() or None
    final_readme = readme_text.strip() or seed_readme or None
    final_summary = seed_summary or final_description
    normalized_text = "\n\n".join(
        [part for part in [final_description, final_summary, final_readme] if part]
    )

    return {
        "name": final_name,
        "slug": generate_slug(final_name),
        "source_url": source_url,
        "repo_url": repo_url,
        "repo_owner": repo_owner,
        "repo_name": repo_name,
        "author": author,
        "description": final_description,
        "readme_summary": final_summary,
        "category": category,
        "stars": github_metadata.stars or seed_stars,
        "last_repo_updated_at": _parse_datetime(github_metadata.updated_at) or seed_updated_at,
        "install_method": install_method,
        "raw_manifest": raw_manifest,
        "raw_readme": final_readme,
        "normalized_text": normalized_text or None,
        "tags": seed_tags,
    }
