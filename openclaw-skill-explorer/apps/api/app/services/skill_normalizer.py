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


def normalize_skill_data(
    seed_item: dict,
    github_metadata: RepoMetadata,
    readme_text: str,
) -> dict:
    seed_name = str(seed_item.get("name") or "").strip()
    repo_url = str(seed_item.get("repo_url") or "").strip() or None
    seed_description = str(seed_item.get("description") or "").strip() or None
    category = str(seed_item.get("category") or "").strip() or None

    owner_from_url, repo_from_url = extract_owner_repo(repo_url)
    repo_owner = github_metadata.repo_owner or owner_from_url
    repo_name = github_metadata.repo_name or repo_from_url

    final_name = (github_metadata.name or seed_name or repo_name or "Unnamed Skill").strip()
    final_description = (github_metadata.description or seed_description or "").strip() or None
    normalized_text = "\n\n".join([part for part in [final_description, readme_text.strip()] if part])

    return {
        "name": final_name,
        "slug": generate_slug(final_name),
        "repo_url": repo_url,
        "repo_owner": repo_owner,
        "repo_name": repo_name,
        "description": final_description,
        "category": category,
        "stars": github_metadata.stars,
        "last_repo_updated_at": _parse_datetime(github_metadata.updated_at),
        "raw_readme": readme_text or None,
        "normalized_text": normalized_text or None,
    }

