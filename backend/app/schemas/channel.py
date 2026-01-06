"""
Схемы для работы с каналами
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ChannelCreate(BaseModel):
    """Создание нового канала"""
    channel_id: int = Field(
        ..., 
        description="Telegram ID канала (отрицательное число)"
    )
    channel_username: Optional[str] = Field(
        None, 
        max_length=50, 
        description="@username канала (без @)"
    )
    title: str = Field(
        ..., 
        min_length=1, 
        max_length=255, 
        description="Название канала"
    )
    is_active: bool = Field(
        True, 
        description="Активен ли канал"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "channel_id": -1001234567890,
                "channel_username": "vip_channel",
                "title": "VIP Канал",
                "is_active": True
            }
        }
    }


class ChannelUpdate(BaseModel):
    """Обновление канала"""
    channel_id: Optional[int] = Field(
        None, 
        description="Telegram ID канала"
    )
    channel_username: Optional[str] = Field(
        None, 
        max_length=50, 
        description="@username канала"
    )
    title: Optional[str] = Field(
        None, 
        min_length=1, 
        max_length=255, 
        description="Название канала"
    )
    is_active: Optional[bool] = Field(
        None, 
        description="Активен ли канал"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Новое название канала",
                "is_active": False
            }
        }
    }


class ChannelResponse(BaseModel):
    """Информация о канале"""
    id: int = Field(..., description="ID канала в БД")
    channel_id: int = Field(..., description="Telegram ID канала")
    channel_username: Optional[str] = Field(None, description="@username канала")
    title: str = Field(..., description="Название")
    is_active: bool = Field(..., description="Активен")
    created_at: datetime = Field(..., description="Дата создания")
    tariffs_count: int = Field(0, description="Количество тарифов")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "channel_id": -1001234567890,
                "channel_username": "vip_channel",
                "title": "VIP Канал",
                "is_active": True,
                "created_at": "2025-01-06T12:00:00",
                "tariffs_count": 3
            }
        }
    }


class ChannelListResponse(BaseModel):
    """Список каналов"""
    total: int = Field(..., description="Всего каналов")
    items: list[ChannelResponse] = Field(..., description="Список каналов")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "total": 2,
                "items": [
                    {
                        "id": 1,
                        "channel_id": -1001234567890,
                        "channel_username": "vip_channel",
                        "title": "VIP Канал",
                        "is_active": True,
                        "created_at": "2025-01-06T12:00:00",
                        "tariffs_count": 3
                    }
                ]
            }
        }
    }
