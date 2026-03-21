from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.risk import RiskReportOut, ScanRequestText
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


@router.post("/readme", response_model=RiskReportOut)
def scan_readme(payload: ScanRequestText, db: Session = Depends(get_db)) -> RiskReportOut:
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
def scan_manifest(payload: ScanRequestText, db: Session = Depends(get_db)) -> RiskReportOut:
    text = _validate_scan_text(payload.text)
    try:
        report, _ = create_risk_report_from_text(db, input_type="manifest", text=text)
        db.commit()
        db.refresh(report)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="failed to persist risk report")
    return _report_to_response(report)

