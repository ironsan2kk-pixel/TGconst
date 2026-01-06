"""Promocode and PromocodeUse models."""

from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .tariff import Tariff
    from .user import User
    from .payment import Payment


class Promocode(Base, TimestampMixin):
    """Promocode for discounts."""
    
    __tablename__ = "promocodes"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    discount_percent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 0-100
    discount_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)  # Fixed USDT discount
    max_uses: Mapped[int | None] = mapped_column(Integer, nullable=True)  # NULL = unlimited
    used_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    valid_from: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    valid_until: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    tariff_id: Mapped[int | None] = mapped_column(ForeignKey("tariffs.id", ondelete="SET NULL"), nullable=True)  # NULL = all tariffs
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Relationships
    tariff: Mapped["Tariff"] = relationship("Tariff", back_populates="promocodes")
    uses: Mapped[list["PromocodeUse"]] = relationship(
        "PromocodeUse",
        back_populates="promocode",
        cascade="all, delete-orphan"
    )
    payments: Mapped[list["Payment"]] = relationship("Payment", back_populates="promocode")
    
    @property
    def is_valid(self) -> bool:
        """Check if promocode is currently valid."""
        if not self.is_active:
            return False
        
        now = datetime.utcnow()
        
        if self.valid_from and now < self.valid_from:
            return False
        
        if self.valid_until and now > self.valid_until:
            return False
        
        if self.max_uses is not None and self.used_count >= self.max_uses:
            return False
        
        return True
    
    def calculate_discount(self, price: float) -> float:
        """Calculate discounted price."""
        if self.discount_percent > 0:
            discount = price * (self.discount_percent / 100)
            return max(0, price - discount)
        elif self.discount_amount > 0:
            return max(0, price - self.discount_amount)
        return price
    
    def __repr__(self) -> str:
        return f"<Promocode(id={self.id}, code={self.code!r})>"


class PromocodeUse(Base):
    """Record of promocode usage."""
    
    __tablename__ = "promocode_uses"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    promocode_id: Mapped[int] = mapped_column(ForeignKey("promocodes.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    payment_id: Mapped[int | None] = mapped_column(ForeignKey("payments.id", ondelete="SET NULL"), nullable=True)
    used_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    promocode: Mapped["Promocode"] = relationship("Promocode", back_populates="uses")
    user: Mapped["User"] = relationship("User", back_populates="promocode_uses")
    
    def __repr__(self) -> str:
        return f"<PromocodeUse(promocode_id={self.promocode_id}, user_id={self.user_id})>"
