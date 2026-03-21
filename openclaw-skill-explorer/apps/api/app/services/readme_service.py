from __future__ import annotations

from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def fetch_readme(repo_owner: str | None, repo_name: str | None) -> str:
    if not repo_owner or not repo_name:
        return ""

    candidate_branches = ["HEAD", "main", "master"]
    for branch in candidate_branches:
        url = (
            f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/{branch}/README.md"
        )
        request = Request(url, headers={"User-Agent": "openclaw-skill-explorer"}, method="GET")
        try:
            with urlopen(request, timeout=5) as response:
                return response.read().decode("utf-8", errors="ignore")
        except (HTTPError, URLError, TimeoutError):
            continue
    return ""
