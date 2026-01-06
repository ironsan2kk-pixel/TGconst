"""AdminLog model for admin actions logging."""

from sqlalchemy import BigInteger, Integer, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class AdminLog(Base, TimestampMixin):
    """Log of admin actions."""
    
    __tablename__ = "admin_logs"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    admin_telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    target_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON details
    
    def __repr__(self) -> str:
        return f"<AdminLog(id={self.id}, admin={self.admin_telegram_id}, action={self.action!r})>"
