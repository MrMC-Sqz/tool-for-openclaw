#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
API_ROOT = PROJECT_ROOT / "apps" / "api"
os.chdir(API_ROOT)
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from sqlalchemy.orm import Session

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.services.github_service import fetch_repo_metadata
from app.services.readme_service import fetch_readme
from app.services.skill_normalizer import normalize_skill_data
from app.services.skill_service import get_or_create_curated_source, upsert_skill

SEED_FILE_PATH = PROJECT_ROOT / "scripts" / "data" / "skills_seed.json"


def load_seed_items() -> list[dict]:
    with SEED_FILE_PATH.open("r", encoding="utf-8") as seed_file:
        payload = json.load(seed_file)
    if not isinstance(payload, list):
        raise ValueError("Seed file must contain a list of skill items.")
    return [item for item in payload if isinstance(item, dict)]


def sync_once(db: Session) -> dict[str, int]:
    stats = {"total_processed": 0, "inserted": 0, "updated": 0, "failed": 0}
    seed_items = load_seed_items()
    source = get_or_create_curated_source(db)

    for item in seed_items:
        stats["total_processed"] += 1
        try:
            github_metadata = fetch_repo_metadata(item.get("repo_url"))
            readme_text = fetch_readme(github_metadata.repo_owner, github_metadata.repo_name)
            normalized_data = normalize_skill_data(item, github_metadata, readme_text)
            _, action = upsert_skill(db, normalized_data, source_id=source.id)
            if action == "inserted":
                stats["inserted"] += 1
            else:
                stats["updated"] += 1
        except Exception:
            stats["failed"] += 1
    return stats


def main() -> None:
    init_db()
    db = SessionLocal()
    try:
        stats = sync_once(db)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    print(f"total processed: {stats['total_processed']}")
    print(f"inserted: {stats['inserted']}")
    print(f"updated: {stats['updated']}")
    print(f"failed: {stats['failed']}")


if __name__ == "__main__":
    main()
