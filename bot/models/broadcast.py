"""Broadcast model."""

from datetime import datetime
from sqlalchemy import Integer, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from bot.models.base import Base, TimestampMixin


class Broadcast(Base, TimestampMixin):
    """Broadcast message campaign."""
    
    __tablename__ = "broadcasts"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    message_text: Mapped[str] = mapped_column(Text, nullable=False)
    message_photo: Mapped[str | None] = mapped_column(String(255), nullable=True)  # file_id
    buttons_json: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON buttons
    filter_type: Mapped[str] = mapped_column(
        String(20),
        default="all",
        nullable=False
    )  # all, active, inactive
    filter_language: Mapped[str] = mapped_column(
        String(5),
        default="all",
        nullable=False
    )  # all, ru, en
    total_users: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    sent_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20),
        default="draft",
        nullable=False
    )  # draft, running, paused, completed, cancelled
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    @property
    def progress_percent(self) -> float:
        """Get broadcast progress percentage."""
        if self.total_users == 0:
            return 0.0
        return round((self.sent_count + self.failed_count) / self.total_users * 100, 1)
    
    def __repr__(self) -> str:
        return f"<Broadcast(id={self.id}, status={self.status!r})>"
