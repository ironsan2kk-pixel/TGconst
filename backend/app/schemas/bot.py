"""
Схемы для работы с ботами
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class BotCreate(BaseModel):
    """Создание нового бота"""
    name: str = Field(
        ..., 
        min_length=1, 
        max_length=100, 
        description="Название бота"
    )
    bot_token: str = Field(
        ..., 
        min_length=10, 
        max_length=100, 
        description="Токен Telegram бота от @BotFather"
    )
    cryptobot_token: Optional[str] = Field(
        None, 
        max_length=100, 
        description="Токен CryptoBot (@CryptoPay)"
    )
    welcome_message: Optional[str] = Field(
        None, 
        max_length=4000, 
        description="Приветственное сообщение"
    )
    support_url: Optional[str] = Field(
        None, 
        max_length=255, 
        description="Ссылка на поддержку"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "VIP Access Bot",
                "bot_token": "123456789:ABCdefGHI_jklMNOpqrSTUvwxYZ",
                "cryptobot_token": "12345:AABBCCDD",
                "welcome_message": "Добро пожаловать! Выберите канал для покупки доступа.",
                "support_url": "https://t.me/support"
            }
        }
    }


class BotUpdate(BaseModel):
    """Обновление бота"""
    name: Optional[str] = Field(
        None, 
        min_length=1, 
        max_length=100, 
        description="Название бота"
    )
    bot_token: Optional[str] = Field(
        None, 
        min_length=10, 
        max_length=100, 
        description="Токен Telegram бота"
    )
    cryptobot_token: Optional[str] = Field(
        None, 
        max_length=100, 
        description="Токен CryptoBot"
    )
    welcome_message: Optional[str] = Field(
        None, 
        max_length=4000, 
        description="Приветственное сообщение"
    )
    support_url: Optional[str] = Field(
        None, 
        max_length=255, 
        description="Ссылка на поддержку"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Updated Bot Name",
                "welcome_message": "Новое приветствие!"
            }
        }
    }


class BotResponse(BaseModel):
    """Информация о боте"""
    id: int = Field(..., description="ID бота")
    uuid: str = Field(..., description="UUID бота")
    name: str = Field(..., description="Название")
    bot_token: str = Field(..., description="Токен Telegram")
    cryptobot_token: Optional[str] = Field(None, description="Токен CryptoBot")
    welcome_message: Optional[str] = Field(None, description="Приветствие")
    support_url: Optional[str] = Field(None, description="Ссылка поддержки")
    is_active: bool = Field(..., description="Бот запущен")
    process_pid: Optional[int] = Field(None, description="PID процесса")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата обновления")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "name": "VIP Access Bot",
                "bot_token": "123456789:ABCdefGHI_jklMNOpqrSTUvwxYZ",
                "cryptobot_token": "12345:AABBCCDD",
                "welcome_message": "Добро пожаловать!",
                "support_url": "https://t.me/support",
                "is_active": False,
                "process_pid": None,
                "created_at": "2025-01-06T12:00:00",
                "updated_at": "2025-01-06T12:00:00"
            }
        }
    }


class BotListResponse(BaseModel):
    """Список ботов"""
    total: int = Field(..., description="Всего ботов")
    items: list[BotResponse] = Field(..., description="Список ботов")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "total": 2,
                "items": [
                    {
                        "id": 1,
                        "uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                        "name": "VIP Bot",
                        "bot_token": "123:ABC",
                        "is_active": True,
                        "process_pid": 12345,
                        "created_at": "2025-01-06T12:00:00",
                        "updated_at": "2025-01-06T12:00:00"
                    }
                ]
            }
        }
    }


class BotStatusResponse(BaseModel):
    """Статус бота"""
    uuid: str = Field(..., description="UUID бота")
    is_active: bool = Field(..., description="Бот запущен")
    process_pid: Optional[int] = Field(None, description="PID процесса")
    message: str = Field(..., description="Сообщение о статусе")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "is_active": True,
                "process_pid": 12345,
                "message": "Бот успешно запущен"
            }
        }
    }
