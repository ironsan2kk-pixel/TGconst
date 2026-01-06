"""Tariff and TariffChannel models."""

from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import Integer, String, Text, Float, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .channel import Channel
    from .subscription import Subscription
    from .payment import Payment
    from .promocode import Promocode


class Tariff(Base, TimestampMixin):
    """Tariff/subscription plan."""
    
    __tablename__ = "tariffs"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name_ru: Mapped[str] = mapped_column(String(255), nullable=False)
    name_en: Mapped[str] = mapped_column(String(255), nullable=False)
    description_ru: Mapped[str | None] = mapped_column(Text, nullable=True)
    description_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    duration_days: Mapped[int] = mapped_column(Integer, default=30, nullable=False)  # 0 = forever
    trial_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 0 = no trial
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Relationships
    tariff_channels: Mapped[list["TariffChannel"]] = relationship(
        "TariffChannel",
        back_populates="tariff",
        cascade="all, delete-orphan"
    )
    subscriptions: Mapped[list["Subscription"]] = relationship(
        "Subscription",
        back_populates="tariff"
    )
    payments: Mapped[list["Payment"]] = relationship(
        "Payment",
        back_populates="tariff"
    )
    promocodes: Mapped[list["Promocode"]] = relationship(
        "Promocode",
        back_populates="tariff"
    )
    
    def __repr__(self) -> str:
        return f"<Tariff(id={self.id}, name_ru={self.name_ru!r}, price={self.price})>"


class TariffChannel(Base):
    """Many-to-many relationship between Tariff and Channel."""
    
    __tablename__ = "tariff_channels"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tariff_id: Mapped[int] = mapped_column(ForeignKey("tariffs.id", ondelete="CASCADE"), nullable=False)
    channel_id: Mapped[int] = mapped_column(ForeignKey("channels.id", ondelete="CASCADE"), nullable=False)
    
    # Relationships
    tariff: Mapped["Tariff"] = relationship("Tariff", back_populates="tariff_channels")
    channel: Mapped["Channel"] = relationship("Channel", back_populates="tariff_channels")
    
    def __repr__(self) -> str:
        return f"<TariffChannel(tariff_id={self.tariff_id}, channel_id={self.channel_id})>"
