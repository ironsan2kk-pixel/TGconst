"""Package models: Package, PackageOption, PackageChannel."""

from datetime import datetime
from typing import TYPE_CHECKING, List
from sqlalchemy import (
    Integer, String, Text, Boolean, Float, DateTime, 
    ForeignKey, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.models.base import Base, TimestampMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from bot.models.channel import Channel
    from bot.models.subscription import Subscription
    from bot.models.payment import Payment


class Package(Base, TimestampMixin, SoftDeleteMixin):
    """Package of channels with subscription options."""
    
    __tablename__ = "packages"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name_ru: Mapped[str] = mapped_column(String(255), nullable=False)
    name_en: Mapped[str] = mapped_column(String(255), nullable=False)
    description_ru: Mapped[str | None] = mapped_column(Text, nullable=True)
    description_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Relationships
    options: Mapped[List["PackageOption"]] = relationship(
        "PackageOption",
        back_populates="package",
        cascade="all, delete-orphan",
        order_by="PackageOption.sort_order"
    )
    package_channels: Mapped[List["PackageChannel"]] = relationship(
        "PackageChannel",
        back_populates="package",
        cascade="all, delete-orphan"
    )
    subscriptions: Mapped[List["Subscription"]] = relationship(
        "Subscription",
        back_populates="package"
    )
    
    def __repr__(self) -> str:
        return f"<Package(id={self.id}, name_ru={self.name_ru!r})>"


class PackageOption(Base):
    """Subscription option for a package (duration + price)."""
    
    __tablename__ = "package_options"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    package_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("packages.id", ondelete="CASCADE"),
        nullable=False
    )
    duration_days: Mapped[int] = mapped_column(Integer, nullable=False)  # 0 = forever
    price: Mapped[float] = mapped_column(Float, nullable=False)
    trial_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 0, 3, 5, 7
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Relationships
    package: Mapped["Package"] = relationship("Package", back_populates="options")
    subscriptions: Mapped[List["Subscription"]] = relationship(
        "Subscription",
        back_populates="package_option"
    )
    payments: Mapped[List["Payment"]] = relationship(
        "Payment",
        back_populates="package_option"
    )
    
    def __repr__(self) -> str:
        return f"<PackageOption(id={self.id}, days={self.duration_days}, price={self.price})>"


class PackageChannel(Base):
    """Many-to-many relationship between packages and channels."""
    
    __tablename__ = "package_channels"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    package_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("packages.id", ondelete="CASCADE"),
        nullable=False
    )
    channel_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("channels.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Relationships
    package: Mapped["Package"] = relationship("Package", back_populates="package_channels")
    channel: Mapped["Channel"] = relationship("Channel", back_populates="package_channels")
    
    def __repr__(self) -> str:
        return f"<PackageChannel(package_id={self.package_id}, channel_id={self.channel_id})>"
