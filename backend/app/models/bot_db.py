"""
Модели для базы данных каждого бота (bot.db)
- channels: каналы для продажи доступа
- tariffs: тарифы (цены и сроки)
- users: пользователи бота
- subscriptions: подписки пользователей
- payments: платежи
- promocodes: промокоды
- broadcasts: рассылки
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Integer, BigInteger, String, Text, Float, Boolean, DateTime,
    ForeignKey, func, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class Channel(Base):
    """Каналы для продажи доступа"""
    __tablename__ = "channels"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    channel_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    channel_username: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        server_default=func.now(),
        nullable=False
    )
    
    # Relationships
    tariffs: Mapped[list["Tariff"]] = relationship(
        "Tariff", 
        back_populates="channel",
        cascade="all, delete-orphan"
    )
    subscriptions: Mapped[list["Subscription"]] = relationship(
        "Subscription",
        back_populates="channel",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Channel(id={self.id}, title={self.title})>"


class Tariff(Base):
    """Тарифы для каналов"""
    __tablename__ = "tariffs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    channel_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("channels.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    duration_days: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        server_default=func.now(),
        nullable=False
    )
    
    # Relationships
    channel: Mapped["Channel"] = relationship("Channel", back_populates="tariffs")
    subscriptions: Mapped[list["Subscription"]] = relationship(
        "Subscription",
        back_populates="tariff"
    )
    
    __table_args__ = (
        Index("ix_tariffs_channel_active", "channel_id", "is_active"),
    )
    
    def __repr__(self) -> str:
        return f"<Tariff(id={self.id}, name={self.name}, price={self.price})>"


class User(Base):
    """Пользователи бота"""
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        server_default=func.now(),
        nullable=False
    )
    last_activity: Mapped[datetime] = mapped_column(
        DateTime, 
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Relationships
    subscriptions: Mapped[list["Subscription"]] = relationship(
        "Subscription",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    payments: Mapped[list["Payment"]] = relationship(
        "Payment",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    @property
    def full_name(self) -> str:
        """Полное имя пользователя"""
        parts = []
        if self.first_name:
            parts.append(self.first_name)
        if self.last_name:
            parts.append(self.last_name)
        return " ".join(parts) if parts else f"User {self.telegram_id}"
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, telegram_id={self.telegram_id})>"


class Subscription(Base):
    """Подписки пользователей на каналы"""
    __tablename__ = "subscriptions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    channel_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("channels.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    tariff_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("tariffs.id", ondelete="SET NULL"),
        nullable=True
    )
    starts_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    auto_kicked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    notified_expiring: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        server_default=func.now(),
        nullable=False
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="subscriptions")
    channel: Mapped["Channel"] = relationship("Channel", back_populates="subscriptions")
    tariff: Mapped[Optional["Tariff"]] = relationship("Tariff", back_populates="subscriptions")
    
    __table_args__ = (
        Index("ix_subscriptions_active_expires", "is_active", "expires_at"),
        Index("ix_subscriptions_user_channel", "user_id", "channel_id"),
    )
    
    def __repr__(self) -> str:
        return f"<Subscription(id={self.id}, user_id={self.user_id}, expires_at={self.expires_at})>"


class Payment(Base):
    """Платежи пользователей"""
    __tablename__ = "payments"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    subscription_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    invoice_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), 
        default="pending", 
        nullable=False,
        index=True
    )  # pending, paid, expired, cancelled
    promocode_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    discount_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    tariff_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    channel_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        server_default=func.now(),
        nullable=False
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="payments")
    
    __table_args__ = (
        Index("ix_payments_user_status", "user_id", "status"),
    )
    
    def __repr__(self) -> str:
        return f"<Payment(id={self.id}, invoice_id={self.invoice_id}, status={self.status})>"


class Promocode(Base):
    """Промокоды со скидками"""
    __tablename__ = "promocodes"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    discount_percent: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    discount_amount: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_uses: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # null = unlimited
    used_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    valid_from: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    valid_until: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        server_default=func.now(),
        nullable=False
    )
    
    __table_args__ = (
        Index("ix_promocodes_active_valid", "is_active", "valid_until"),
    )
    
    def is_valid(self) -> bool:
        """Проверка валидности промокода"""
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
    
    def calculate_discount(self, original_price: float) -> float:
        """Рассчитать скидку"""
        if self.discount_percent:
            return original_price * (self.discount_percent / 100)
        elif self.discount_amount:
            return min(self.discount_amount, original_price)
        return 0.0
    
    def __repr__(self) -> str:
        return f"<Promocode(id={self.id}, code={self.code})>"


class Broadcast(Base):
    """Рассылки пользователям"""
    __tablename__ = "broadcasts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    message_text: Mapped[str] = mapped_column(Text, nullable=False)
    message_photo: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # file_id или путь
    total_users: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    sent_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), 
        default="pending", 
        nullable=False,
        index=True
    )  # pending, running, completed, cancelled
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        server_default=func.now(),
        nullable=False
    )
    
    @property
    def progress_percent(self) -> float:
        """Процент выполнения рассылки"""
        if self.total_users == 0:
            return 0.0
        return round((self.sent_count + self.failed_count) / self.total_users * 100, 2)
    
    def __repr__(self) -> str:
        return f"<Broadcast(id={self.id}, status={self.status})>"
