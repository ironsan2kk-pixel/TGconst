"""Payment model."""

from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import (
    Integer, BigInteger, String, Text, Float, DateTime,
    ForeignKey, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from bot.models.user import User
    from bot.models.package import PackageOption
    from bot.models.subscription import Subscription
    from bot.models.promocode import Promocode


class Payment(Base, TimestampMixin):
    """Crypto payment record."""
    
    __tablename__ = "payments"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    package_option_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("package_options.id", ondelete="SET NULL"),
        nullable=True
    )
    subscription_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("subscriptions.id", ondelete="SET NULL"),
        nullable=True
    )
    network: Mapped[str] = mapped_column(String(20), nullable=False)  # ton / trc20
    wallet_address: Mapped[str] = mapped_column(String(100), nullable=False)
    tx_hash: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    original_amount: Mapped[float | None] = mapped_column(Float, nullable=True)  # Before discount
    promocode_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("promocodes.id", ondelete="SET NULL"),
        nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False
    )  # pending, checking, confirmed, failed, manual
    payment_method: Mapped[str] = mapped_column(
        String(20),
        default="crypto",
        nullable=False
    )  # crypto / manual
    confirmed_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)  # Admin telegram_id
    check_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="payments")
    package_option: Mapped["PackageOption"] = relationship(
        "PackageOption",
        back_populates="payments"
    )
    subscription: Mapped["Subscription"] = relationship(
        "Subscription",
        back_populates="payment"
    )
    promocode: Mapped["Promocode"] = relationship("Promocode")
    
    def __repr__(self) -> str:
        return f"<Payment(id={self.id}, amount={self.amount}, status={self.status!r})>"
