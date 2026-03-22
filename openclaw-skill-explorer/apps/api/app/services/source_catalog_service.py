from __future__ import annotations

import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.services.catalog_generator import generate_public_catalog
from app.services.github_service import search_repositories

PROJECT_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_SOURCE_CONFIG_PATH = PROJECT_ROOT / "scripts" / "data" / "public_source_configs.json"


def load_public_source_configs(path: Path | None = None) -> list[dict]:
    config_path = path or DEFAULT_SOURCE_CONFIG_PATH
    if not config_path.exists():
        return []
    with config_path.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    if not isinstance(payload, list):
        raise ValueError("Public source config must be a list.")
    return [item for item in payload if isinstance(item, dict)]


def fetch_source_items(source_config: dict) -> list[dict]:
    source_type = str(source_config.get("type") or "").strip().lower()
    if source_type == "github_search":
        return _fetch_github_search_items(source_config)
    if source_type == "remote_json":
        return _fetch_remote_json_items(source_config)
    if source_type == "generated_catalog":
        return generate_public_catalog(int(source_config.get("count") or 120))
    return []


def _fetch_github_search_items(source_config: dict) -> list[dict]:
    query = str(source_config.get("query") or "").strip()
    if not query:
        return []
    category = str(source_config.get("category") or "").strip().lower() or None
    tag_hints = [str(tag).strip().lower() for tag in source_config.get("tag_hints", []) if str(tag).strip()]
    max_results = max(1, min(60, int(source_config.get("max_results") or 20)))

    items = []
    for repo in search_repositories(query, max_results=max_results):
        tags = []
        for tag in [*tag_hints, category, repo.repo_owner, repo.repo_name]:
            normalized = str(tag or "").strip().lower()
            if normalized and normalized not in tags:
                tags.append(normalized)

        items.append(
            {
                "name": repo.name or repo.repo_name or "Unnamed Public Skill",
                "repo_url": repo.repo_url,
                "category": category,
                "description": repo.description or f"Public repository discovered for query: {query}",
                "readme_summary": repo.description or f"Public GitHub repository matched for query: {query}",
                "tags": tags,
                "stars": repo.stars,
                "last_repo_updated_at": repo.updated_at,
                "author": repo.repo_owner,
                "install_method": "git",
                "source_url": "https://api.github.com/search/repositories",
                "offline_only": True,
            }
        )
    return items


def _fetch_remote_json_items(source_config: dict) -> list[dict]:
    url = str(source_config.get("url") or "").strip()
    if not url:
        return []
    request = Request(url, headers={"User-Agent": "openclaw-skill-explorer"}, method="GET")
    try:
        with urlopen(request, timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError):
        return []

    if not isinstance(payload, list):
        return []
    return [item for item in payload if isinstance(item, dict)]
