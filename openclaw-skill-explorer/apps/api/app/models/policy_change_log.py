from datetime import datetime

from sqlalchemy import DateTime, Integer, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PolicyChangeLog(Base):
    __tablename__ = "policy_change_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    policy_version: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    change_type: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("'system'"))
    related_feedback_count: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    published_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, index=True, server_default=func.current_timestamp()
    )
