from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.skill import Skill


class RiskReport(Base):
    __tablename__ = "risk_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    skill_id: Mapped[int | None] = mapped_column(
        ForeignKey("skills.id", ondelete="CASCADE"), nullable=True, index=True
    )
    input_type: Mapped[str] = mapped_column(Text, nullable=False)
    risk_level: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    risk_score: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))

    file_read: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    file_write: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    network_access: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    shell_exec: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    secrets_access: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    external_download: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    app_access: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    unclear_docs: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))

    permissions_detected: Mapped[str | None] = mapped_column(Text, nullable=True)
    sensitive_scopes: Mapped[str | None] = mapped_column(Text, nullable=True)
    findings_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommendations: Mapped[str | None] = mapped_column(Text, nullable=True)

    scanned_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, index=True, server_default=func.current_timestamp()
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.current_timestamp()
    )

    skill: Mapped["Skill | None"] = relationship("Skill", back_populates="risk_reports")
