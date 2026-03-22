from datetime import datetime

from pydantic import BaseModel

from app.schemas.risk import RiskReportOut


class SkillListItem(BaseModel):
    name: str
    slug: str
    description: str | None
    category: str | None
    stars: int
    last_repo_updated_at: datetime | None
    risk_level: str | None = None
    relevance_score: int | None = None
    review_state: str = "pending_review"
    latest_reviewer: str | None = None


class SkillListResponse(BaseModel):
    items: list[SkillListItem]
    total: int
    page: int
    page_size: int


class SkillDetailResponse(BaseModel):
    name: str
    slug: str
    repo_url: str | None
    repo_owner: str | None
    repo_name: str | None
    description: str | None
    category: str | None
    stars: int
    last_repo_updated_at: datetime | None
    readme_summary: str | None
    latest_risk_report: RiskReportOut | None
    review_state: str = "pending_review"


class SimilarSkillsResponse(BaseModel):
    items: list[SkillListItem]


class SkillReviewCreateRequest(BaseModel):
    reviewer: str = "system"
    decision: str
    comment: str | None = None
    override_reason: str | None = None


class SkillReviewOut(BaseModel):
    id: int
    reviewer: str
    decision: str
    comment: str | None
    override_reason: str | None
    created_at: datetime


class SkillReviewListResponse(BaseModel):
    items: list[SkillReviewOut]


class SkillAuditLogOut(BaseModel):
    id: int
    action_type: str
    actor: str
    payload_json: str | None
    created_at: datetime


class SkillAuditLogListResponse(BaseModel):
    items: list[SkillAuditLogOut]


class RemediationChecklistItemOut(BaseModel):
    capability: str
    priority: int
    title: str
    guidance: str


class RemediationChecklistResponse(BaseModel):
    review_state: str = "pending_review"
    risk_level: str | None = None
    items: list[RemediationChecklistItemOut]


class ScanDeltaResponse(BaseModel):
    previous_report_id: int
    current_report_id: int
    previous_scanned_at: datetime
    current_scanned_at: datetime
    previous_policy_version: str
    current_policy_version: str
    previous_risk_level: str
    current_risk_level: str
    previous_risk_score: int
    current_risk_score: int
    score_delta: int
    added_flags: list[str]
    removed_flags: list[str]
    persisted_flags: list[str]


class ReviewSummaryItemOut(BaseModel):
    review_id: int
    skill_slug: str
    reviewer: str
    decision: str
    created_at: datetime


class ReviewSummaryResponse(BaseModel):
    total_reviews: int
    by_decision: dict[str, int]
    by_reviewer: dict[str, int]
    recent_items: list[ReviewSummaryItemOut]
