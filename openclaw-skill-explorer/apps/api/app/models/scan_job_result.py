from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.risk_report import RiskReport
    from app.models.scan_job import ScanJob


class ScanJobResult(Base):
    __tablename__ = "scan_job_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(
        ForeignKey("scan_jobs.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )
    risk_report_id: Mapped[int | None] = mapped_column(
        ForeignKey("risk_reports.id", ondelete="SET NULL"), nullable=True, index=True
    )
    stats_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.current_timestamp()
    )

    job: Mapped["ScanJob"] = relationship("ScanJob", back_populates="result")
    risk_report: Mapped["RiskReport | None"] = relationship("RiskReport")
