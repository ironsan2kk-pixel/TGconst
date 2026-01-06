"""
Pydantic схемы для рассылок.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class ButtonItem(BaseModel):
    """Кнопка."""
    text: str = Field(..., min_length=1, max_length=64)
    url: str | None = Field(None, max_length=512)
    callback_data: str | None = Field(None, max_length=64)


class BroadcastCreate(BaseModel):
    """Создание рассылки."""
    message_text: str = Field(..., min_length=1, max_length=4096)
    message_photo: str | None = Field(None, max_length=255)
    buttons: list[list[ButtonItem]] | None = None
    filter_type: str = Field("all", pattern=r"^(all|active|inactive|tariff_\d+)$")
    filter_language: Literal["all", "ru", "en"] = "all"
    scheduled_at: datetime | None = None
    
    @field_validator("buttons")
    @classmethod
    def validate_buttons(cls, v):
        if v is None:
            return v
        if len(v) > 10:
            raise ValueError("Maximum 10 rows of buttons")
        for row in v:
            if len(row) > 3:
                raise ValueError("Maximum 3 buttons per row")
        return v


class BroadcastUpdate(BaseModel):
    """Обновление рассылки."""
    message_text: str | None = Field(None, min_length=1, max_length=4096)
    message_photo: str | None = Field(None, max_length=255)
    buttons: list[list[ButtonItem]] | None = None
    filter_type: str | None = Field(None, pattern=r"^(all|active|inactive|tariff_\d+)$")
    filter_language: Literal["all", "ru", "en"] | None = None
    scheduled_at: datetime | None = None
    
    @field_validator("buttons")
    @classmethod
    def validate_buttons(cls, v):
        if v is None:
            return v
        if len(v) > 10:
            raise ValueError("Maximum 10 rows of buttons")
        for row in v:
            if len(row) > 3:
                raise ValueError("Maximum 3 buttons per row")
        return v


class BroadcastResponse(BaseModel):
    """Ответ с рассылкой."""
    id: int
    message_text: str
    message_photo: str | None
    buttons_json: str | None
    filter_type: str
    filter_language: str
    total_users: int
    sent_count: int
    failed_count: int
    status: str
    scheduled_at: datetime | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    progress_percent: float
    
    class Config:
        from_attributes = True


class BroadcastListResponse(BaseModel):
    """Список рассылок."""
    items: list[BroadcastResponse]
    total: int
    limit: int
    offset: int


class BroadcastCountResponse(BaseModel):
    """Количество получателей."""
    count: int
    filter_type: str
    filter_language: str


class BroadcastStatusResponse(BaseModel):
    """Статус рассылки."""
    id: int
    status: str
    sent_count: int
    failed_count: int
    total_users: int
    progress_percent: float


class QuickBroadcastRequest(BaseModel):
    """Быстрая рассылка."""
    message_text: str = Field(..., min_length=1, max_length=4096)
    filter_type: str = Field("all", pattern=r"^(all|active|inactive|tariff_\d+)$")
    filter_language: Literal["all", "ru", "en"] = "all"


class QuickBroadcastResponse(BaseModel):
    """Результат быстрой рассылки."""
    sent: int
    failed: int
    total: int
