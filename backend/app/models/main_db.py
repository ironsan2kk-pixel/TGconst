"""
Модели для главной базы данных (main.db)
- admins: администраторы системы
- bots: список созданных ботов
- userbot_config: конфигурация Pyrogram userbot
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Integer, String, Text, Boolean, DateTime, 
    func, Index
)
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class Admin(Base):
    """Администраторы системы"""
    __tablename__ = "admins"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        server_default=func.now(),
        nullable=False
    )
    
    def __repr__(self) -> str:
        return f"<Admin(id={self.id}, username={self.username})>"


class Bot(Base):
    """Созданные боты"""
    __tablename__ = "bots"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    uuid: Mapped[str] = mapped_column(String(36), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    bot_token: Mapped[str] = mapped_column(String(100), nullable=False)
    cryptobot_token: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    welcome_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    support_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    process_pid: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    __table_args__ = (
        Index("ix_bots_is_active", "is_active"),
    )
    
    def __repr__(self) -> str:
        return f"<Bot(id={self.id}, uuid={self.uuid}, name={self.name})>"


class UserbotConfig(Base):
    """Конфигурация Pyrogram userbot для добавления/кика пользователей"""
    __tablename__ = "userbot_config"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    api_id: Mapped[int] = mapped_column(Integer, nullable=False)
    api_hash: Mapped[str] = mapped_column(String(50), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    session_string: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    def __repr__(self) -> str:
        return f"<UserbotConfig(id={self.id}, phone={self.phone})>"
