from __future__ import annotations

import json
import re
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.core.config import settings

GITHUB_REPO_PATTERN = re.compile(r"^https?://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/#?]+)")


@dataclass
class RepoMetadata:
    repo_owner: str | None = None
    repo_name: str | None = None
    name: str | None = None
    description: str | None = None
    stars: int = 0
    updated_at: str | None = None


def extract_owner_repo(repo_url: str | None) -> tuple[str | None, str | None]:
    if not repo_url:
        return None, None

    match = GITHUB_REPO_PATTERN.match(repo_url.strip())
    if not match:
        return None, None

    owner = match.group("owner").strip()
    repo = match.group("repo").strip()
    if repo.endswith(".git"):
        repo = repo[:-4]
    return owner, repo


def fetch_repo_metadata(repo_url: str | None) -> RepoMetadata:
    owner, repo = extract_owner_repo(repo_url)
    metadata = RepoMetadata(repo_owner=owner, repo_name=repo)
    if not owner or not repo:
        return metadata

    api_url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "openclaw-skill-explorer",
    }
    if settings.github_token:
        headers["Authorization"] = f"Bearer {settings.github_token}"

    request = Request(api_url, headers=headers, method="GET")
    try:
        with urlopen(request, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError):
        return metadata

    metadata.name = payload.get("name")
    metadata.description = payload.get("description")
    metadata.stars = int(payload.get("stargazers_count") or 0)
    metadata.updated_at = payload.get("updated_at")
    owner_payload = payload.get("owner") or {}
    metadata.repo_owner = owner_payload.get("login") or metadata.repo_owner
    metadata.repo_name = payload.get("name") or metadata.repo_name
    return metadata
