from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.skill import Skill


class SkillReview(Base):
    __tablename__ = "skill_reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    skill_id: Mapped[int] = mapped_column(
        ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True
    )
    reviewer: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("'system'"))
    decision: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    override_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, index=True, server_default=func.current_timestamp()
    )

    skill: Mapped["Skill"] = relationship("Skill", back_populates="reviews")
