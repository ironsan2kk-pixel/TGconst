"""Subscription model."""

from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import (
    Integer, BigInteger, String, Boolean, DateTime, 
    ForeignKey, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from bot.models.user import User
    from bot.models.package import Package, PackageOption
    from bot.models.payment import Payment


class Subscription(Base, TimestampMixin):
    """User subscription to a package."""
    
    __tablename__ = "subscriptions"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    package_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("packages.id", ondelete="SET NULL"),
        nullable=True
    )
    package_option_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("package_options.id", ondelete="SET NULL"),
        nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="active",
        nullable=False
    )  # active, expired, cancelled, trial
    starts_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)  # NULL = forever
    auto_kicked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    notified_3days: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    notified_1day: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    granted_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)  # Admin telegram_id
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="subscriptions")
    package: Mapped["Package"] = relationship("Package", back_populates="subscriptions")
    package_option: Mapped["PackageOption"] = relationship(
        "PackageOption",
        back_populates="subscriptions"
    )
    payment: Mapped["Payment"] = relationship(
        "Payment",
        back_populates="subscription",
        uselist=False
    )
    
    @property
    def is_active(self) -> bool:
        """Check if subscription is currently active."""
        if self.status not in ("active", "trial"):
            return False
        if self.expires_at is None:
            return True
        return datetime.utcnow() < self.expires_at
    
    def __repr__(self) -> str:
        return f"<Subscription(id={self.id}, user_id={self.user_id}, status={self.status!r})>"
