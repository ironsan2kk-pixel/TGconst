"""
Схемы для работы с промокодами
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator


class PromocodeCreate(BaseModel):
    """Создание нового промокода"""
    code: str = Field(
        ..., 
        min_length=1, 
        max_length=50, 
        description="Код промокода (уникальный)"
    )
    discount_percent: Optional[int] = Field(
        None, 
        ge=1, 
        le=100, 
        description="Скидка в процентах (1-100)"
    )
    discount_amount: Optional[float] = Field(
        None, 
        gt=0, 
        description="Фиксированная скидка в USD"
    )
    max_uses: Optional[int] = Field(
        None, 
        ge=1, 
        description="Максимальное количество использований (null = безлимит)"
    )
    valid_from: Optional[datetime] = Field(
        None, 
        description="Дата начала действия промокода"
    )
    valid_until: Optional[datetime] = Field(
        None, 
        description="Дата окончания действия промокода"
    )
    is_active: bool = Field(
        True, 
        description="Активен ли промокод"
    )
    
    @field_validator('code')
    @classmethod
    def uppercase_code(cls, v: str) -> str:
        """Приводим код к верхнему регистру"""
        return v.strip().upper()
    
    @field_validator('discount_amount')
    @classmethod
    def round_discount_amount(cls, v: float | None) -> float | None:
        """Округляем фикс. скидку до 2 знаков"""
        if v is not None:
            return round(v, 2)
        return v
    
    @model_validator(mode='after')
    def check_discount(self):
        """Проверяем что указана хотя бы одна скидка"""
        if self.discount_percent is None and self.discount_amount is None:
            raise ValueError('Необходимо указать discount_percent или discount_amount')
        if self.discount_percent is not None and self.discount_amount is not None:
            raise ValueError('Укажите только discount_percent ИЛИ discount_amount, не оба')
        return self
    
    @model_validator(mode='after')
    def check_dates(self):
        """Проверяем что даты валидны"""
        if self.valid_from and self.valid_until:
            if self.valid_from >= self.valid_until:
                raise ValueError('valid_from должна быть раньше valid_until')
        return self
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "code": "SAVE20",
                "discount_percent": 20,
                "max_uses": 100,
                "valid_until": "2025-12-31T23:59:59",
                "is_active": True
            }
        }
    }


class PromocodeUpdate(BaseModel):
    """Обновление промокода"""
    code: Optional[str] = Field(
        None, 
        min_length=1, 
        max_length=50, 
        description="Код промокода"
    )
    discount_percent: Optional[int] = Field(
        None, 
        ge=1, 
        le=100, 
        description="Скидка в процентах"
    )
    discount_amount: Optional[float] = Field(
        None, 
        gt=0, 
        description="Фиксированная скидка в USD"
    )
    max_uses: Optional[int] = Field(
        None, 
        ge=1, 
        description="Максимальное количество использований"
    )
    valid_from: Optional[datetime] = Field(
        None, 
        description="Дата начала действия"
    )
    valid_until: Optional[datetime] = Field(
        None, 
        description="Дата окончания действия"
    )
    is_active: Optional[bool] = Field(
        None, 
        description="Активен ли промокод"
    )
    
    @field_validator('code')
    @classmethod
    def uppercase_code(cls, v: str | None) -> str | None:
        """Приводим код к верхнему регистру"""
        if v is not None:
            return v.strip().upper()
        return v
    
    @field_validator('discount_amount')
    @classmethod
    def round_discount_amount(cls, v: float | None) -> float | None:
        """Округляем фикс. скидку до 2 знаков"""
        if v is not None:
            return round(v, 2)
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "discount_percent": 25,
                "max_uses": 200,
                "is_active": True
            }
        }
    }


class PromocodeResponse(BaseModel):
    """Информация о промокоде"""
    id: int = Field(..., description="ID промокода в БД")
    code: str = Field(..., description="Код промокода")
    discount_percent: Optional[int] = Field(None, description="Скидка %")
    discount_amount: Optional[float] = Field(None, description="Фикс. скидка USD")
    max_uses: Optional[int] = Field(None, description="Лимит использований")
    used_count: int = Field(..., description="Использовано раз")
    valid_from: Optional[datetime] = Field(None, description="Действует с")
    valid_until: Optional[datetime] = Field(None, description="Действует до")
    is_active: bool = Field(..., description="Активен")
    is_valid: bool = Field(..., description="Можно использовать сейчас")
    created_at: datetime = Field(..., description="Дата создания")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "code": "SAVE20",
                "discount_percent": 20,
                "discount_amount": None,
                "max_uses": 100,
                "used_count": 15,
                "valid_from": None,
                "valid_until": "2025-12-31T23:59:59",
                "is_active": True,
                "is_valid": True,
                "created_at": "2025-01-06T12:00:00"
            }
        }
    }


class PromocodeListResponse(BaseModel):
    """Список промокодов"""
    total: int = Field(..., description="Всего промокодов")
    active_count: int = Field(..., description="Активных промокодов")
    items: list[PromocodeResponse] = Field(..., description="Список промокодов")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "total": 5,
                "active_count": 3,
                "items": [
                    {
                        "id": 1,
                        "code": "SAVE20",
                        "discount_percent": 20,
                        "discount_amount": None,
                        "max_uses": 100,
                        "used_count": 15,
                        "valid_from": None,
                        "valid_until": "2025-12-31T23:59:59",
                        "is_active": True,
                        "is_valid": True,
                        "created_at": "2025-01-06T12:00:00"
                    }
                ]
            }
        }
    }


class PromocodeValidateRequest(BaseModel):
    """Запрос на проверку промокода"""
    code: str = Field(
        ..., 
        min_length=1, 
        max_length=50,
        description="Код промокода для проверки"
    )
    price: Optional[float] = Field(
        None, 
        gt=0, 
        description="Цена для расчёта скидки (опционально)"
    )
    
    @field_validator('code')
    @classmethod
    def uppercase_code(cls, v: str) -> str:
        """Приводим код к верхнему регистру"""
        return v.strip().upper()
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "code": "SAVE20",
                "price": 9.99
            }
        }
    }


class PromocodeValidateResponse(BaseModel):
    """Результат проверки промокода"""
    valid: bool = Field(..., description="Промокод валиден")
    code: str = Field(..., description="Код промокода")
    discount_percent: Optional[int] = Field(None, description="Скидка %")
    discount_amount: Optional[float] = Field(None, description="Фикс. скидка USD")
    calculated_discount: Optional[float] = Field(None, description="Рассчитанная скидка (если указана цена)")
    final_price: Optional[float] = Field(None, description="Итоговая цена со скидкой")
    error: Optional[str] = Field(None, description="Причина невалидности")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "valid": True,
                "code": "SAVE20",
                "discount_percent": 20,
                "discount_amount": None,
                "calculated_discount": 2.0,
                "final_price": 7.99,
                "error": None
            }
        }
    }


class PromocodeClearLimitRequest(BaseModel):
    """Запрос на сброс лимита использований"""
    reset_count: bool = Field(
        True,
        description="Сбросить счётчик использований в 0"
    )
    new_max_uses: Optional[int] = Field(
        None,
        ge=1,
        description="Новый лимит использований (null = безлимит)"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "reset_count": True,
                "new_max_uses": 100
            }
        }
    }
