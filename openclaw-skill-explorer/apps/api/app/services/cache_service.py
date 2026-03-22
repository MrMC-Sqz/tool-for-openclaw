from __future__ import annotations

import json
import time
from threading import Lock
from typing import Any

_CACHE_LOCK = Lock()
_CACHE_STORE: dict[str, tuple[float, Any]] = {}


def make_cache_key(prefix: str, payload: dict[str, Any]) -> str:
    return f"{prefix}:{json.dumps(payload, sort_keys=True, default=str, ensure_ascii=True)}"


def get_cache(key: str) -> Any | None:
    now = time.time()
    with _CACHE_LOCK:
        entry = _CACHE_STORE.get(key)
        if not entry:
            return None
        expires_at, value = entry
        if expires_at <= now:
            _CACHE_STORE.pop(key, None)
            return None
        return value


def set_cache(key: str, value: Any, ttl_seconds: int) -> None:
    expires_at = time.time() + max(1, ttl_seconds)
    with _CACHE_LOCK:
        _CACHE_STORE[key] = (expires_at, value)


def invalidate_prefix(prefix: str) -> int:
    removed = 0
    with _CACHE_LOCK:
        keys = [key for key in _CACHE_STORE if key.startswith(prefix)]
        for key in keys:
            _CACHE_STORE.pop(key, None)
            removed += 1
    return removed

