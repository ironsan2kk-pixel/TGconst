"""
Схемы для работы с рассылками
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class BroadcastCreate(BaseModel):
    """Создание новой рассылки"""
    message_text: str = Field(
        ..., 
        min_length=1, 
        max_length=4096, 
        description="Текст сообщения для рассылки"
    )
    message_photo: Optional[str] = Field(
        None, 
        max_length=255, 
        description="File ID фото или путь к файлу (опционально)"
    )
    
    @field_validator('message_text')
    @classmethod
    def strip_text(cls, v: str) -> str:
        """Убираем лишние пробелы"""
        return v.strip()
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "message_text": "🎉 Привет всем!\n\nУ нас отличные новости...",
                "message_photo": None
            }
        }
    }


class BroadcastUpdate(BaseModel):
    """Обновление рассылки (только для pending)"""
    message_text: Optional[str] = Field(
        None, 
        min_length=1, 
        max_length=4096, 
        description="Текст сообщения"
    )
    message_photo: Optional[str] = Field(
        None, 
        max_length=255, 
        description="File ID фото или путь к файлу"
    )
    
    @field_validator('message_text')
    @classmethod
    def strip_text(cls, v: str | None) -> str | None:
        """Убираем лишние пробелы"""
        if v is not None:
            return v.strip()
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "message_text": "📢 Обновлённый текст рассылки"
            }
        }
    }


class BroadcastResponse(BaseModel):
    """Информация о рассылке"""
    id: int = Field(..., description="ID рассылки в БД")
    message_text: str = Field(..., description="Текст сообщения")
    message_photo: Optional[str] = Field(None, description="Фото (file_id или путь)")
    total_users: int = Field(..., description="Всего пользователей для рассылки")
    sent_count: int = Field(..., description="Успешно отправлено")
    failed_count: int = Field(..., description="Не удалось отправить")
    status: str = Field(..., description="Статус: pending, running, completed, cancelled")
    progress_percent: float = Field(..., description="Процент выполнения")
    started_at: Optional[datetime] = Field(None, description="Время начала")
    completed_at: Optional[datetime] = Field(None, description="Время завершения")
    created_at: datetime = Field(..., description="Время создания")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "message_text": "🎉 Привет всем!\n\nУ нас отличные новости...",
                "message_photo": None,
                "total_users": 150,
                "sent_count": 145,
                "failed_count": 5,
                "status": "completed",
                "progress_percent": 100.0,
                "started_at": "2025-01-06T12:00:00",
                "completed_at": "2025-01-06T12:05:32",
                "created_at": "2025-01-06T11:58:00"
            }
        }
    }


class BroadcastListResponse(BaseModel):
    """Список рассылок"""
    total: int = Field(..., description="Всего рассылок")
    pending_count: int = Field(..., description="Ожидают запуска")
    running_count: int = Field(..., description="Выполняются сейчас")
    completed_count: int = Field(..., description="Завершённых")
    items: list[BroadcastResponse] = Field(..., description="Список рассылок")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "total": 10,
                "pending_count": 2,
                "running_count": 1,
                "completed_count": 7,
                "items": []
            }
        }
    }


class BroadcastStartResponse(BaseModel):
    """Ответ на запуск рассылки"""
    success: bool = Field(..., description="Успешно ли запущена рассылка")
    message: str = Field(..., description="Сообщение о результате")
    broadcast: BroadcastResponse = Field(..., description="Обновлённая информация о рассылке")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "message": "Рассылка запущена. Всего получателей: 150",
                "broadcast": {
                    "id": 1,
                    "message_text": "🎉 Привет!",
                    "message_photo": None,
                    "total_users": 150,
                    "sent_count": 0,
                    "failed_count": 0,
                    "status": "running",
                    "progress_percent": 0.0,
                    "started_at": "2025-01-06T12:00:00",
                    "completed_at": None,
                    "created_at": "2025-01-06T11:58:00"
                }
            }
        }
    }


class BroadcastCancelResponse(BaseModel):
    """Ответ на отмену рассылки"""
    success: bool = Field(..., description="Успешно ли отменена рассылка")
    message: str = Field(..., description="Сообщение о результате")
    broadcast: BroadcastResponse = Field(..., description="Обновлённая информация о рассылке")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "message": "Рассылка отменена. Отправлено 50 из 150 сообщений.",
                "broadcast": {
                    "id": 1,
                    "message_text": "🎉 Привет!",
                    "message_photo": None,
                    "total_users": 150,
                    "sent_count": 50,
                    "failed_count": 3,
                    "status": "cancelled",
                    "progress_percent": 35.33,
                    "started_at": "2025-01-06T12:00:00",
                    "completed_at": "2025-01-06T12:02:15",
                    "created_at": "2025-01-06T11:58:00"
                }
            }
        }
    }


class BroadcastStatsResponse(BaseModel):
    """Статистика по рассылкам"""
    total_broadcasts: int = Field(..., description="Всего рассылок")
    total_sent: int = Field(..., description="Всего отправлено сообщений")
    total_failed: int = Field(..., description="Всего неудачных отправок")
    pending: int = Field(..., description="Ожидают запуска")
    running: int = Field(..., description="Выполняются")
    completed: int = Field(..., description="Завершены")
    cancelled: int = Field(..., description="Отменены")
    success_rate: float = Field(..., description="Процент успешных отправок")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "total_broadcasts": 25,
                "total_sent": 3500,
                "total_failed": 150,
                "pending": 2,
                "running": 1,
                "completed": 20,
                "cancelled": 2,
                "success_rate": 95.89
            }
        }
    }
