"""Task model for userbot queue."""

from datetime import datetime
from sqlalchemy import Integer, BigInteger, String, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from bot.models.base import Base, TimestampMixin


class Task(Base, TimestampMixin):
    """Task queue for userbot (invite/kick)."""
    
    __tablename__ = "tasks"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # invite / kick
    user_telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    channel_id: Mapped[int] = mapped_column(BigInteger, nullable=False)  # Telegram channel ID
    payload: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON extra data
    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False
    )  # pending, processing, completed, failed
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    def __repr__(self) -> str:
        return f"<Task(id={self.id}, type={self.type!r}, status={self.status!r})>"
