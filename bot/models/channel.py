"""Channel model."""

from datetime import datetime
from typing import TYPE_CHECKING, List
from sqlalchemy import BigInteger, String, Text, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.models.base import Base, TimestampMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from bot.models.package import PackageChannel


class Channel(Base, TimestampMixin, SoftDeleteMixin):
    """Telegram channel."""
    
    __tablename__ = "channels"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    channel_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str | None] = mapped_column(String(100), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    invite_link: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Relationships
    package_channels: Mapped[List["PackageChannel"]] = relationship(
        "PackageChannel",
        back_populates="channel",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Channel(id={self.id}, title={self.title!r})>"
