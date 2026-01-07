"""User model."""

from datetime import datetime
from typing import TYPE_CHECKING, List
from sqlalchemy import BigInteger, String, Text, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from bot.models.subscription import Subscription
    from bot.models.payment import Payment
    from bot.models.promocode import PromocodeUse


class User(Base, TimestampMixin):
    """Telegram user."""
    
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str | None] = mapped_column(String(100), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    language: Mapped[str] = mapped_column(String(5), default="ru", nullable=False)
    trial_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ban_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_activity: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    subscriptions: Mapped[List["Subscription"]] = relationship(
        "Subscription",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    payments: Mapped[List["Payment"]] = relationship(
        "Payment",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    promocode_uses: Mapped[List["PromocodeUse"]] = relationship(
        "PromocodeUse",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        parts = [self.first_name, self.last_name]
        return " ".join(p for p in parts if p) or "Unknown"
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, telegram_id={self.telegram_id})>"
