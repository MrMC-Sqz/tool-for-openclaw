#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
API_ROOT = PROJECT_ROOT / "apps" / "api"
os.chdir(API_ROOT)
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.services.skill_service import get_or_create_curated_source
from app.services.sync_service import build_empty_stats, sync_once, write_sync_report


def main() -> None:
    init_db()
    db = SessionLocal()
    status = "failed"
    source_name = "unknown"
    stats = build_empty_stats()
    try:
        stats, status, source_name = sync_once(db)
        db.commit()
    except Exception:  # noqa: BLE001
        db.rollback()
        try:
            source = get_or_create_curated_source(db)
            source.sync_status = "failed"
            source.last_synced_at = datetime.utcnow()
            db.commit()
        except Exception:  # noqa: BLE001
            db.rollback()
        raise
    finally:
        db.close()

    report_path = write_sync_report(stats, status=status, source_name=source_name)
    print(f"status: {status}")
    print(f"source files: {stats['source_files']}")
    print(f"total raw items: {stats['total_raw']}")
    print(f"invalid items skipped: {stats['invalid_items']}")
    print(f"duplicate items skipped: {stats['duplicate_items']}")
    print(f"total processed: {stats['total_processed']}")
    print(f"inserted: {stats['inserted']}")
    print(f"updated: {stats['updated']}")
    print(f"failed: {stats['failed']}")
    print(f"failed validation: {stats['failed_validation']}")
    print(f"failed db: {stats['failed_db']}")
    print(f"failed unexpected: {stats['failed_unexpected']}")
    print(f"report: {report_path}")


if __name__ == "__main__":
    main()
