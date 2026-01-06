"""
Схемы для работы с тарифами
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class TariffCreate(BaseModel):
    """Создание нового тарифа"""
    name: str = Field(
        ..., 
        min_length=1, 
        max_length=100, 
        description="Название тарифа"
    )
    price: float = Field(
        ..., 
        gt=0, 
        description="Цена в USD"
    )
    duration_days: int = Field(
        ..., 
        gt=0, 
        description="Срок подписки в днях"
    )
    is_active: bool = Field(
        True, 
        description="Активен ли тариф"
    )
    sort_order: int = Field(
        0, 
        ge=0, 
        description="Порядок сортировки"
    )
    
    @field_validator('price')
    @classmethod
    def round_price(cls, v: float) -> float:
        """Округляем цену до 2 знаков после запятой"""
        return round(v, 2)
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "1 месяц",
                "price": 9.99,
                "duration_days": 30,
                "is_active": True,
                "sort_order": 1
            }
        }
    }


class TariffUpdate(BaseModel):
    """Обновление тарифа"""
    name: Optional[str] = Field(
        None, 
        min_length=1, 
        max_length=100, 
        description="Название тарифа"
    )
    price: Optional[float] = Field(
        None, 
        gt=0, 
        description="Цена в USD"
    )
    duration_days: Optional[int] = Field(
        None, 
        gt=0, 
        description="Срок подписки в днях"
    )
    is_active: Optional[bool] = Field(
        None, 
        description="Активен ли тариф"
    )
    sort_order: Optional[int] = Field(
        None, 
        ge=0, 
        description="Порядок сортировки"
    )
    
    @field_validator('price')
    @classmethod
    def round_price(cls, v: float | None) -> float | None:
        """Округляем цену до 2 знаков после запятой"""
        if v is not None:
            return round(v, 2)
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "2 месяца",
                "price": 14.99,
                "is_active": True
            }
        }
    }


class TariffResponse(BaseModel):
    """Информация о тарифе"""
    id: int = Field(..., description="ID тарифа в БД")
    channel_id: int = Field(..., description="ID канала (FK)")
    name: str = Field(..., description="Название")
    price: float = Field(..., description="Цена USD")
    duration_days: int = Field(..., description="Срок (дни)")
    is_active: bool = Field(..., description="Активен")
    sort_order: int = Field(..., description="Сортировка")
    created_at: datetime = Field(..., description="Дата создания")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "channel_id": 1,
                "name": "1 месяц",
                "price": 9.99,
                "duration_days": 30,
                "is_active": True,
                "sort_order": 1,
                "created_at": "2025-01-06T12:00:00"
            }
        }
    }


class TariffListResponse(BaseModel):
    """Список тарифов"""
    total: int = Field(..., description="Всего тарифов")
    channel_id: int = Field(..., description="ID канала")
    items: list[TariffResponse] = Field(..., description="Список тарифов")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "total": 3,
                "channel_id": 1,
                "items": [
                    {
                        "id": 1,
                        "channel_id": 1,
                        "name": "1 месяц",
                        "price": 9.99,
                        "duration_days": 30,
                        "is_active": True,
                        "sort_order": 1,
                        "created_at": "2025-01-06T12:00:00"
                    }
                ]
            }
        }
    }
