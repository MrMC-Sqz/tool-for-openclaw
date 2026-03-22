from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.security import require_roles
from app.db.session import get_db
from app.models.risk_report import RiskReport
from app.schemas.risk import RiskReportOut, ScanRequestText
from app.schemas.job import ScanJobCreateResponse, ScanJobOut, ScanJobResultOut
from app.services.job_service import (
    create_scan_job,
    enqueue_scan_job,
    get_scan_job,
    parse_scan_job_stats,
)
from app.services.risk_service import create_risk_report_from_text, risk_report_to_scan_result

router = APIRouter(prefix="/api/scan", tags=["scan"])


def _validate_scan_text(text: str) -> str:
    trimmed = text.strip()
    if not trimmed:
        raise HTTPException(status_code=400, detail="text must not be empty")
    return trimmed


def _report_to_response(report) -> RiskReportOut:
    scan_result = risk_report_to_scan_result(report)
    return RiskReportOut(
        id=report.id,
        skill_id=report.skill_id,
        input_type=report.input_type,
        scanned_at=report.scanned_at,
        **scan_result,
    )


def _build_job_response(db: Session, job_id: int) -> ScanJobOut:
    job = get_scan_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="scan job not found")

    risk_report_out: RiskReportOut | None = None
    if job.result and job.result.risk_report_id:
        report = db.query(RiskReport).filter(RiskReport.id == job.result.risk_report_id).first()
        if report:
            payload = risk_report_to_scan_result(report)
            risk_report_out = RiskReportOut(
                id=report.id,
                skill_id=report.skill_id,
                input_type=report.input_type,
                scanned_at=report.scanned_at,
                **payload,
            )

    parsed_stats = parse_scan_job_stats(job)
    result = None
    if risk_report_out or parsed_stats is not None:
        result = ScanJobResultOut(risk_report=risk_report_out, stats=parsed_stats)

    return ScanJobOut(
        id=job.id,
        skill_id=job.skill_id,
        status=job.status,
        input_type=job.input_type,
        input_value=job.input_value,
        error_message=job.error_message,
        created_at=job.created_at,
        started_at=job.started_at,
        finished_at=job.finished_at,
        result=result,
    )


@router.post("/readme", response_model=RiskReportOut)
def scan_readme(
    payload: ScanRequestText,
    _role: str = Depends(require_roles("reviewer", "admin")),
    db: Session = Depends(get_db),
) -> RiskReportOut:
    text = _validate_scan_text(payload.text)
    try:
        report, _ = create_risk_report_from_text(db, input_type="readme", text=text)
        db.commit()
        db.refresh(report)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="failed to persist risk report")
    return _report_to_response(report)


@router.post("/manifest", response_model=RiskReportOut)
def scan_manifest(
    payload: ScanRequestText,
    _role: str = Depends(require_roles("reviewer", "admin")),
    db: Session = Depends(get_db),
) -> RiskReportOut:
    text = _validate_scan_text(payload.text)
    try:
        report, _ = create_risk_report_from_text(db, input_type="manifest", text=text)
        db.commit()
        db.refresh(report)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="failed to persist risk report")
    return _report_to_response(report)


@router.post("/readme/jobs", response_model=ScanJobCreateResponse)
def submit_readme_scan_job(
    payload: ScanRequestText,
    _role: str = Depends(require_roles("reviewer", "admin")),
    db: Session = Depends(get_db),
) -> ScanJobCreateResponse:
    text = _validate_scan_text(payload.text)
    try:
        job = create_scan_job(db, input_type="readme", input_value=text)
        db.commit()
        db.refresh(job)
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc))
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="failed to create scan job")

    enqueue_scan_job(job.id)
    return ScanJobCreateResponse(job_id=job.id, status=job.status)


@router.post("/manifest/jobs", response_model=ScanJobCreateResponse)
def submit_manifest_scan_job(
    payload: ScanRequestText,
    _role: str = Depends(require_roles("reviewer", "admin")),
    db: Session = Depends(get_db),
) -> ScanJobCreateResponse:
    text = _validate_scan_text(payload.text)
    try:
        job = create_scan_job(db, input_type="manifest", input_value=text)
        db.commit()
        db.refresh(job)
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc))
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="failed to create scan job")

    enqueue_scan_job(job.id)
    return ScanJobCreateResponse(job_id=job.id, status=job.status)


@router.post("/sync/jobs", response_model=ScanJobCreateResponse)
def submit_sync_job(
    _role: str = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
) -> ScanJobCreateResponse:
    try:
        job = create_scan_job(db, input_type="sync_sources")
        db.commit()
        db.refresh(job)
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc))
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="failed to create sync job")

    enqueue_scan_job(job.id)
    return ScanJobCreateResponse(job_id=job.id, status=job.status)


@router.get("/jobs/{job_id}", response_model=ScanJobOut)
def get_job(
    job_id: int,
    _role: str = Depends(require_roles("viewer", "reviewer", "admin")),
    db: Session = Depends(get_db),
) -> ScanJobOut:
    return _build_job_response(db, job_id)
