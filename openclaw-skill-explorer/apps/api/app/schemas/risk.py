from datetime import datetime

from pydantic import BaseModel


class ScanRequestText(BaseModel):
    text: str


class RiskFlags(BaseModel):
    file_read: bool
    file_write: bool
    network_access: bool
    shell_exec: bool
    secrets_access: bool
    external_download: bool
    app_access: bool
    unclear_docs: bool


class ScanResponse(BaseModel):
    policy_version: str = "v1.0.0"
    risk_level: str
    risk_score: int
    explanation: str
    flags: RiskFlags
    matched_keywords: dict[str, list[str]]
    evidence_snippets: list[str] = []
    reasons: list[str]
    recommendations: list[str]


class RiskReportOut(ScanResponse):
    id: int
    skill_id: int | None
    input_type: str
    scanned_at: datetime
