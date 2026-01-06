"""
Схемы для авторизации
"""
from datetime import datetime
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Запрос на авторизацию"""
    username: str = Field(..., min_length=1, max_length=50, description="Логин")
    password: str = Field(..., min_length=1, description="Пароль")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "admin",
                "password": "admin123"
            }
        }
    }


class TokenResponse(BaseModel):
    """Ответ с токеном доступа"""
    access_token: str = Field(..., description="JWT токен")
    token_type: str = Field(default="bearer", description="Тип токена")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }
    }


class AdminResponse(BaseModel):
    """Информация об администраторе"""
    id: int = Field(..., description="ID администратора")
    username: str = Field(..., description="Логин")
    created_at: datetime = Field(..., description="Дата создания")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "username": "admin",
                "created_at": "2025-01-06T12:00:00"
            }
        }
    }
