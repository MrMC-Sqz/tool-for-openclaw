from __future__ import annotations

from functools import lru_cache
from typing import Callable

from fastapi import Depends, Header, HTTPException, status

from app.core.config import settings

ALLOWED_ROLES = {"viewer", "reviewer", "admin"}


@lru_cache(maxsize=1)
def _token_role_map() -> dict[str, str]:
    token_map: dict[str, str] = {}
    for raw_entry in [item.strip() for item in settings.auth_api_keys.split(",") if item.strip()]:
        if ":" not in raw_entry:
            continue
        role, token = raw_entry.split(":", 1)
        normalized_role = role.strip().lower()
        normalized_token = token.strip()
        if normalized_role not in ALLOWED_ROLES or not normalized_token:
            continue
        token_map[normalized_token] = normalized_role
    return token_map


def get_current_role(x_api_key: str | None = Header(default=None, alias="X-API-Key")) -> str:
    if not settings.auth_enabled:
        return "admin"

    token_map = _token_role_map()
    if not token_map:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="auth is enabled but AUTH_API_KEYS is not configured",
        )
    if not x_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="missing api key")

    role = token_map.get(x_api_key.strip())
    if not role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid api key")
    return role


def require_roles(*allowed_roles: str) -> Callable:
    normalized_roles = {role.strip().lower() for role in allowed_roles if role.strip()}
    invalid_roles = normalized_roles - ALLOWED_ROLES
    if invalid_roles:
        invalid_text = ",".join(sorted(invalid_roles))
        raise ValueError(f"unsupported role(s): {invalid_text}")

    def _guard(role: str = Depends(get_current_role)) -> str:
        if role not in normalized_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")
        return role

    return _guard
