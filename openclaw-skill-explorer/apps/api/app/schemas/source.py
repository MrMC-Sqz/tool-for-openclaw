from datetime import datetime

from pydantic import BaseModel


class SourceListItem(BaseModel):
    id: int
    name: str
    type: str
    base_url: str | None
    is_active: int
    sync_status: str
    last_synced_at: datetime | None
    updated_at: datetime | None
    skill_count: int


class SourceListResponse(BaseModel):
    items: list[SourceListItem]
