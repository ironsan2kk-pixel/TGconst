"""Payment model."""

from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import BigInteger, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .user import User
    from .tariff import Tariff
    from .subscription import Subscription
    from .promocode import Promocode


class Payment(Base, TimestampMixin):
    """Payment record."""
    
    __tablename__ = "payments"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    tariff_id: Mapped[int] = mapped_column(ForeignKey("tariffs.id", ondelete="SET NULL"), nullable=True)
    subscription_id: Mapped[int | None] = mapped_column(ForeignKey("subscriptions.id", ondelete="SET NULL"), nullable=True)
    invoice_id: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True)  # CryptoBot invoice ID
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    original_amount: Mapped[float | None] = mapped_column(Float, nullable=True)  # Before discount
    promocode_id: Mapped[int | None] = mapped_column(ForeignKey("promocodes.id", ondelete="SET NULL"), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)  # pending/paid/expired/cancelled/manual
    payment_method: Mapped[str] = mapped_column(String(20), default="cryptobot", nullable=False)  # cryptobot/manual
    confirmed_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)  # Admin telegram_id for manual
    paid_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="payments")
    tariff: Mapped["Tariff"] = relationship("Tariff", back_populates="payments")
    subscription: Mapped["Subscription"] = relationship("Subscription", back_populates="payments")
    promocode: Mapped["Promocode"] = relationship("Promocode", back_populates="payments")
    
    def __repr__(self) -> str:
        return f"<Payment(id={self.id}, user_id={self.user_id}, amount={self.amount}, status={self.status!r})>"
