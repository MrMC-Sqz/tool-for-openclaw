from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.skill import Skill


class SkillAuditLog(Base):
    __tablename__ = "skill_audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    skill_id: Mapped[int] = mapped_column(
        ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True
    )
    action_type: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    actor: Mapped[str] = mapped_column(Text, nullable=False)
    payload_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, index=True, server_default=func.current_timestamp()
    )

    skill: Mapped["Skill"] = relationship("Skill", back_populates="audit_logs")
