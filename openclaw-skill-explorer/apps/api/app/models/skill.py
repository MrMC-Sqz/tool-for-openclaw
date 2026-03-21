from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.risk_report import RiskReport
    from app.models.scan_job import ScanJob
    from app.models.source import Source
    from app.models.tag import Tag


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_id: Mapped[int | None] = mapped_column(
        ForeignKey("sources.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    slug: Mapped[str] = mapped_column(Text, nullable=False, unique=True, index=True)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    repo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    repo_owner: Mapped[str | None] = mapped_column(Text, nullable=True)
    repo_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    author: Mapped[str | None] = mapped_column(Text, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    readme_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(Text, nullable=True, index=True)
    stars: Mapped[int] = mapped_column(Integer, nullable=False, index=True, server_default=text("0"))
    last_repo_updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, index=True)
    install_method: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_manifest: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_readme: Mapped[str | None] = mapped_column(Text, nullable=True)
    normalized_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_featured: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    is_archived: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.current_timestamp()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.current_timestamp()
    )

    source: Mapped["Source | None"] = relationship("Source", back_populates="skills")
    risk_reports: Mapped[list["RiskReport"]] = relationship(
        "RiskReport", back_populates="skill", cascade="all, delete-orphan"
    )
    scan_jobs: Mapped[list["ScanJob"]] = relationship(
        "ScanJob", back_populates="skill", cascade="all, delete-orphan"
    )
    tags: Mapped[list["Tag"]] = relationship("Tag", secondary="skill_tags", back_populates="skills")
