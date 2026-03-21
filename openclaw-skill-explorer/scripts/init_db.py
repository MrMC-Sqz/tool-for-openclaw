#!/usr/bin/env python3
"""Initialize local SQLite database placeholder for development."""

from pathlib import Path
import sqlite3

DEFAULT_DB_PATH = Path("openclaw_skill_explorer.db")


def main() -> None:
    DEFAULT_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DEFAULT_DB_PATH)
    connection.execute("PRAGMA user_version = 1;")
    connection.commit()
    connection.close()
    print(f"Initialized SQLite placeholder at: {DEFAULT_DB_PATH.resolve()}")


if __name__ == "__main__":
    main()
