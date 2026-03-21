import sqlite3
from pathlib import Path

from app.core.config import settings


def _resolve_sqlite_path(database_url: str) -> Path:
    prefix = "sqlite:///"
    if not database_url.startswith(prefix):
        raise ValueError("Only sqlite URLs are supported in the initialization scaffold.")
    raw = database_url[len(prefix):]
    return Path(raw)


def get_sqlite_connection() -> sqlite3.Connection:
    db_path = _resolve_sqlite_path(settings.database_url)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    return connection
