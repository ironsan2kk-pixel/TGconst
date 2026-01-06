"""Subscription model."""

from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .user import User
    from .tariff import Tariff
    from .payment import Payment


class Subscription(Base, TimestampMixin):
    """User subscription to a tariff."""
    
    __tablename__ = "subscriptions"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    tariff_id: Mapped[int] = mapped_column(ForeignKey("tariffs.id", ondelete="CASCADE"), nullable=False)
    is_trial: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    starts_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)  # NULL = forever
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    auto_kicked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    notified_3days: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    notified_1day: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    granted_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)  # Admin telegram_id
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="subscriptions")
    tariff: Mapped["Tariff"] = relationship("Tariff", back_populates="subscriptions")
    payments: Mapped[list["Payment"]] = relationship("Payment", back_populates="subscription")
    
    @property
    def is_expired(self) -> bool:
        """Check if subscription is expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_forever(self) -> bool:
        """Check if subscription is forever."""
        return self.expires_at is None
    
    def __repr__(self) -> str:
        return f"<Subscription(id={self.id}, user_id={self.user_id}, tariff_id={self.tariff_id})>"
