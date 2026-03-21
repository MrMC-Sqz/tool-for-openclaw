from datetime import datetime

from pydantic import BaseModel


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

