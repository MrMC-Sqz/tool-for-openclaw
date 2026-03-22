from __future__ import annotations

from threading import Lock
from typing import Any

_LOCK = Lock()
_TOTAL_REQUESTS = 0
_TOTAL_ERRORS = 0
_TOTAL_DURATION_MS = 0.0
_ROUTE_COUNTERS: dict[str, dict[str, Any]] = {}


def record_request(method: str, path: str, status_code: int, duration_ms: float) -> None:
    global _TOTAL_REQUESTS, _TOTAL_ERRORS, _TOTAL_DURATION_MS
    key = f"{method.upper()} {path}"
    with _LOCK:
        _TOTAL_REQUESTS += 1
        _TOTAL_DURATION_MS += max(0.0, duration_ms)
        if status_code >= 500:
            _TOTAL_ERRORS += 1

        route_stats = _ROUTE_COUNTERS.setdefault(
            key,
            {
                "count": 0,
                "errors": 0,
                "total_duration_ms": 0.0,
            },
        )
        route_stats["count"] += 1
        route_stats["total_duration_ms"] += max(0.0, duration_ms)
        if status_code >= 500:
            route_stats["errors"] += 1


def snapshot_metrics() -> dict[str, Any]:
    with _LOCK:
        average_duration_ms = (_TOTAL_DURATION_MS / _TOTAL_REQUESTS) if _TOTAL_REQUESTS > 0 else 0.0
        by_route = {
            route: {
                "count": values["count"],
                "errors": values["errors"],
                "avg_duration_ms": (
                    values["total_duration_ms"] / values["count"] if values["count"] > 0 else 0.0
                ),
            }
            for route, values in sorted(_ROUTE_COUNTERS.items())
        }
        return {
            "total_requests": _TOTAL_REQUESTS,
            "total_errors": _TOTAL_ERRORS,
            "avg_duration_ms": average_duration_ms,
            "by_route": by_route,
        }

