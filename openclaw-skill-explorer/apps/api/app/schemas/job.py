from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel

from app.schemas.risk import RiskReportOut


class ScanJobCreateResponse(BaseModel):
    job_id: int
    status: str


class ScanJobResultOut(BaseModel):
    risk_report: RiskReportOut | None = None
    stats: dict[str, Any] | None = None


class ScanJobOut(BaseModel):
    id: int
    skill_id: int | None
    status: str
    input_type: str
    input_value: str | None
    error_message: str | None
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
    result: ScanJobResultOut | None = None
