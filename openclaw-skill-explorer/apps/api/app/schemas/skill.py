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
