from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.risk_report import RiskReport
    from app.models.skill import Skill


class SkillFeedback(Base):
    __tablename__ = "skill_feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    skill_id: Mapped[int] = mapped_column(
        ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True
    )
    risk_report_id: Mapped[int | None] = mapped_column(
        ForeignKey("risk_reports.id", ondelete="SET NULL"), nullable=True, index=True
    )
    reporter: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("'system'"))
    feedback_type: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    severity: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("'medium'"))
    status: Mapped[str] = mapped_column(Text, nullable=False, index=True, server_default=text("'open'"))
    expected_risk_level: Mapped[str | None] = mapped_column(Text, nullable=True)
    actual_risk_level: Mapped[str | None] = mapped_column(Text, nullable=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, index=True, server_default=func.current_timestamp()
    )

    skill: Mapped["Skill"] = relationship("Skill", back_populates="feedback_items")
    risk_report: Mapped["RiskReport | None"] = relationship("RiskReport")
