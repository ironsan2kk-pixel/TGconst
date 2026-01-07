"""Admin log model."""

from sqlalchemy import Integer, BigInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from bot.models.base import Base, TimestampMixin


class AdminLog(Base, TimestampMixin):
    """Admin action log."""
    
    __tablename__ = "admin_logs"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    admin_telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    target_user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)  # users.id
    details: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON details
    
    def __repr__(self) -> str:
        return f"<AdminLog(id={self.id}, action={self.action!r})>"
