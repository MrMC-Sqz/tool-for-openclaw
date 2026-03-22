from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import json
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session, selectinload

from app.db.session import SessionLocal
from app.models.scan_job import ScanJob
from app.models.scan_job_result import ScanJobResult
from app.models.skill import Skill
from app.services.cache_service import invalidate_prefix
from app.services.risk_service import create_risk_report_for_skill, create_risk_report_from_text
from app.services.sync_service import sync_once, sync_source_by_name, write_sync_report

SCAN_JOB_INPUT_TYPES = {"readme", "manifest", "skill", "sync_sources", "sync_source"}
SCAN_JOB_TERMINAL_STATUSES = {"succeeded", "failed"}
JOB_EXECUTOR = ThreadPoolExecutor(max_workers=4, thread_name_prefix="scan-job")


def create_scan_job(
    db: Session,
    *,
    input_type: str,
    input_value: str | None = None,
    skill_id: int | None = None,
) -> ScanJob:
    normalized_input_type = input_type.strip().lower()
    if normalized_input_type not in SCAN_JOB_INPUT_TYPES:
        raise ValueError(f"unsupported input_type: {input_type}")

    normalized_input_value = input_value.strip() if input_value is not None else None
    if normalized_input_type in {"readme", "manifest"} and not normalized_input_value:
        raise ValueError("input_value must not be empty for text scan jobs")
    if normalized_input_type == "skill" and skill_id is None:
        raise ValueError("skill_id is required for skill scan jobs")
    if normalized_input_type == "sync_sources":
        has_active_sync_job = (
            db.query(ScanJob.id)
            .filter(
                ScanJob.input_type.in_(("sync_sources", "sync_source")),
                ScanJob.status.in_(("pending", "running")),
            )
            .first()
        )
        if has_active_sync_job:
            raise ValueError("a sync job is already pending or running")
    if normalized_input_type == "sync_source":
        if not normalized_input_value:
            raise ValueError("input_value must not be empty for source sync jobs")
        has_active_sync_job = (
            db.query(ScanJob.id)
            .filter(
                ScanJob.input_type.in_(("sync_sources", "sync_source")),
                ScanJob.status.in_(("pending", "running")),
            )
            .first()
        )
        if has_active_sync_job:
            raise ValueError("a sync job is already pending or running")

    job = ScanJob(
        skill_id=skill_id,
        status="pending",
        input_type=normalized_input_type,
        input_value=normalized_input_value,
    )
    db.add(job)
    db.flush()
    return job


def get_scan_job(db: Session, job_id: int) -> ScanJob | None:
    return (
        db.query(ScanJob)
        .options(selectinload(ScanJob.result))
        .filter(ScanJob.id == job_id)
        .first()
    )


def parse_scan_job_stats(job: ScanJob) -> dict[str, Any] | None:
    if not job.result or not job.result.stats_json:
        return None
    try:
        parsed = json.loads(job.result.stats_json)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def run_scan_job(job_id: int) -> None:
    db = SessionLocal()
    try:
        job = db.query(ScanJob).filter(ScanJob.id == job_id).first()
        if not job:
            return
        if job.status in SCAN_JOB_TERMINAL_STATUSES:
            return

        job.status = "running"
        job.started_at = job.started_at or datetime.utcnow()
        job.error_message = None
        db.commit()

        risk_report_id: int | None = None
        stats_payload: dict[str, Any] | None = None

        if job.input_type in {"readme", "manifest"}:
            text = (job.input_value or "").strip()
            if not text:
                raise ValueError("scan text is empty")
            report, _ = create_risk_report_from_text(db, input_type=job.input_type, text=text)
            risk_report_id = report.id
            stats_payload = {
                "risk_level": report.risk_level,
                "risk_score": report.risk_score,
                "policy_version": "v1.0.0",
            }
        elif job.input_type == "skill":
            if job.skill_id is None:
                raise ValueError("skill scan job missing skill_id")
            skill = db.query(Skill).filter(Skill.id == job.skill_id).first()
            if not skill:
                raise ValueError("skill not found")
            report, _ = create_risk_report_for_skill(db, skill)
            risk_report_id = report.id
            stats_payload = {
                "risk_level": report.risk_level,
                "risk_score": report.risk_score,
                "policy_version": "v1.0.0",
            }
        elif job.input_type == "sync_sources":
            stats, sync_status, source_name = sync_once(db)
            report_path = write_sync_report(stats, status=sync_status, source_name=source_name)
            stats_payload = {
                "sync_status": sync_status,
                "source_name": source_name,
                "stats": stats,
                "report_path": str(report_path),
            }
        elif job.input_type == "sync_source":
            source_name = (job.input_value or "").strip()
            if not source_name:
                raise ValueError("source sync job missing source name")
            stats, sync_status, synced_source_name = sync_source_by_name(db, source_name=source_name)
            report_path = write_sync_report(stats, status=sync_status, source_name=synced_source_name)
            stats_payload = {
                "sync_status": sync_status,
                "source_name": synced_source_name,
                "stats": stats,
                "report_path": str(report_path),
            }
        else:
            raise ValueError(f"unsupported job input_type: {job.input_type}")

        _upsert_job_result(
            db,
            job_id=job.id,
            risk_report_id=risk_report_id,
            stats_payload=stats_payload,
        )
        if job.input_type == "skill":
            skill_slug = None
            if job.skill_id is not None:
                skill = db.query(Skill).filter(Skill.id == job.skill_id).first()
                skill_slug = skill.slug if skill else None
            invalidate_prefix("skills:list:")
            if skill_slug:
                invalidate_prefix(f"skills:detail:{skill_slug}:")
            else:
                invalidate_prefix("skills:detail:")
        elif job.input_type in {"sync_sources", "sync_source"}:
            invalidate_prefix("skills:list:")
            invalidate_prefix("skills:detail:")

        job.status = "succeeded"
        job.finished_at = datetime.utcnow()
        job.error_message = None
        db.commit()
    except Exception as exc:  # noqa: BLE001
        db.rollback()
        _mark_job_failed(db, job_id=job_id, error_message=str(exc))
    finally:
        db.close()


def enqueue_scan_job(job_id: int) -> None:
    JOB_EXECUTOR.submit(run_scan_job, job_id)


def _upsert_job_result(
    db: Session,
    *,
    job_id: int,
    risk_report_id: int | None,
    stats_payload: dict[str, Any] | None,
) -> None:
    existing = db.query(ScanJobResult).filter(ScanJobResult.job_id == job_id).first()
    payload_text = json.dumps(stats_payload, ensure_ascii=True) if stats_payload is not None else None
    if existing:
        existing.risk_report_id = risk_report_id
        existing.stats_json = payload_text
        db.flush()
        return

    db.add(
        ScanJobResult(
            job_id=job_id,
            risk_report_id=risk_report_id,
            stats_json=payload_text,
        )
    )
    db.flush()


def _mark_job_failed(db: Session, *, job_id: int, error_message: str) -> None:
    try:
        job = db.query(ScanJob).filter(ScanJob.id == job_id).first()
        if not job:
            return
        job.status = "failed"
        job.started_at = job.started_at or datetime.utcnow()
        job.finished_at = datetime.utcnow()
        job.error_message = error_message[:500]
        db.commit()
    except Exception:  # noqa: BLE001
        db.rollback()
