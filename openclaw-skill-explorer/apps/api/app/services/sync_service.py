from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import TypedDict

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.services.github_service import fetch_repo_metadata
from app.services.readme_service import fetch_readme
from app.services.skill_normalizer import normalize_skill_data
from app.services.skill_service import get_or_create_curated_source, upsert_skill

PROJECT_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_SEED_FILE_PATH = PROJECT_ROOT / "scripts" / "data" / "skills_seed.json"
DEFAULT_SEED_FILE_GLOB = "skills_seed*.json"
DEFAULT_REPORT_DIR = PROJECT_ROOT / "scripts" / "reports"


class SeedLoadResult(TypedDict):
    items: list[dict]
    total_raw: int
    invalid_items: int
    duplicate_items: int
    source_files: int


class SyncStats(TypedDict):
    source_files: int
    total_raw: int
    invalid_items: int
    duplicate_items: int
    total_processed: int
    inserted: int
    updated: int
    failed: int
    failed_validation: int
    failed_db: int
    failed_unexpected: int


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _build_dedupe_key(item: dict) -> str:
    repo_url = str(item.get("repo_url") or "").strip().lower()
    slug = str(item.get("slug") or "").strip().lower()
    name = str(item.get("name") or "").strip().lower()

    if repo_url:
        return f"repo:{repo_url}"
    if slug:
        return f"slug:{slug}"
    if name:
        return f"name:{name}"
    return f"raw:{json.dumps(item, sort_keys=True, ensure_ascii=True)}"


def discover_seed_files(
    seed_file_glob: str = DEFAULT_SEED_FILE_GLOB,
    default_seed_path: Path = DEFAULT_SEED_FILE_PATH,
) -> list[Path]:
    override_path = os.getenv("SEED_FILE_PATH", "").strip()
    if override_path:
        candidate = Path(override_path)
        if not candidate.is_absolute():
            candidate = PROJECT_ROOT / candidate
        return [candidate]

    data_dir = PROJECT_ROOT / "scripts" / "data"
    files = sorted(data_dir.glob(seed_file_glob))
    if not files and default_seed_path.exists():
        return [default_seed_path]
    return files


def load_seed_items() -> SeedLoadResult:
    seed_files = discover_seed_files()
    if not seed_files:
        raise FileNotFoundError("No seed source files found.")

    combined_items: list[dict] = []
    dedupe_keys: set[str] = set()
    total_raw = 0
    invalid_items = 0
    duplicate_items = 0

    for seed_path in seed_files:
        if not seed_path.exists():
            continue
        with seed_path.open("r", encoding="utf-8") as seed_file:
            payload = json.load(seed_file)
        if not isinstance(payload, list):
            raise ValueError(f"Seed file must contain a list of skill items: {seed_path}")

        for item in payload:
            total_raw += 1
            if not isinstance(item, dict):
                invalid_items += 1
                continue
            dedupe_key = _build_dedupe_key(item)
            if dedupe_key in dedupe_keys:
                duplicate_items += 1
                continue
            dedupe_keys.add(dedupe_key)
            combined_items.append(item)

    return {
        "items": combined_items,
        "total_raw": total_raw,
        "invalid_items": invalid_items,
        "duplicate_items": duplicate_items,
        "source_files": len(seed_files),
    }


def classify_error(exc: Exception) -> str:
    if isinstance(exc, ValueError):
        return "validation"
    if isinstance(exc, SQLAlchemyError):
        return "db"
    return "unexpected"


def process_item(db: Session, item: dict, source_id: int) -> str:
    repo_url = str(item.get("repo_url") or "").strip()
    if not repo_url:
        raise ValueError("Missing repo_url")

    github_metadata = fetch_repo_metadata(repo_url)
    readme_text = fetch_readme(github_metadata.repo_owner, github_metadata.repo_name)
    normalized_data = normalize_skill_data(item, github_metadata, readme_text)
    _, action = upsert_skill(db, normalized_data, source_id=source_id)
    return action


def execute_with_retry(
    db: Session,
    item: dict,
    source_id: int,
    max_retries: int,
    retry_delay_seconds: float,
) -> str:
    last_error: Exception | None = None
    for attempt in range(1, max_retries + 2):
        try:
            return process_item(db, item, source_id)
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if classify_error(exc) != "db" or attempt > max_retries:
                break
            time.sleep(retry_delay_seconds * attempt)
    if last_error is None:
        raise RuntimeError("Unknown sync failure")
    raise last_error


def build_empty_stats() -> SyncStats:
    return {
        "source_files": 0,
        "total_raw": 0,
        "invalid_items": 0,
        "duplicate_items": 0,
        "total_processed": 0,
        "inserted": 0,
        "updated": 0,
        "failed": 0,
        "failed_validation": 0,
        "failed_db": 0,
        "failed_unexpected": 0,
    }


def write_sync_report(stats: SyncStats, status: str, source_name: str) -> Path:
    DEFAULT_REPORT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    report_path = DEFAULT_REPORT_DIR / f"sync_report_{timestamp}.json"
    payload = {
        "generated_at": utc_now_iso(),
        "status": status,
        "source_name": source_name,
        "stats": stats,
        "health": {
            "success_rate": (
                round(
                    ((stats["total_processed"] - stats["failed"]) / stats["total_processed"]) * 100,
                    2,
                )
                if stats["total_processed"] > 0
                else 0.0
            ),
            "duplicate_rate": (
                round((stats["duplicate_items"] / stats["total_raw"]) * 100, 2)
                if stats["total_raw"] > 0
                else 0.0
            ),
            "invalid_rate": (
                round((stats["invalid_items"] / stats["total_raw"]) * 100, 2)
                if stats["total_raw"] > 0
                else 0.0
            ),
        },
    }
    report_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")
    return report_path


def sync_once(
    db: Session,
    max_retries: int = 2,
    retry_delay_seconds: float = 0.5,
) -> tuple[SyncStats, str, str]:
    stats = build_empty_stats()
    seed_result = load_seed_items()
    stats["source_files"] = seed_result["source_files"]
    stats["total_raw"] = seed_result["total_raw"]
    stats["invalid_items"] = seed_result["invalid_items"]
    stats["duplicate_items"] = seed_result["duplicate_items"]

    source = get_or_create_curated_source(db)
    source.sync_status = "running"
    db.flush()

    for item in seed_result["items"]:
        stats["total_processed"] += 1
        try:
            action = execute_with_retry(
                db,
                item,
                source.id,
                max_retries=max_retries,
                retry_delay_seconds=retry_delay_seconds,
            )
            if action == "inserted":
                stats["inserted"] += 1
            else:
                stats["updated"] += 1
        except Exception as exc:  # noqa: BLE001
            stats["failed"] += 1
            category = classify_error(exc)
            if category == "validation":
                stats["failed_validation"] += 1
            elif category == "db":
                stats["failed_db"] += 1
            else:
                stats["failed_unexpected"] += 1

    source.last_synced_at = datetime.utcnow()
    source.sync_status = "partial" if stats["failed"] > 0 else "success"
    db.flush()
    return stats, source.sync_status, source.name

