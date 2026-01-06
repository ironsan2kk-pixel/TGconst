"""
Зависимости (dependencies) для FastAPI роутеров
"""
from typing import AsyncGenerator, Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_main_db
from ..models.main_db import Admin
from ..utils.security import decode_access_token

# Схема авторизации через Bearer token
security = HTTPBearer(
    scheme_name="Bearer",
    description="JWT токен авторизации",
    auto_error=True
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency для получения сессии главной БД.
    Это обёртка над get_main_db для удобства.
    """
    async for session in get_main_db():
        yield session


async def get_current_admin(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> Admin:
    """
    Dependency для получения текущего авторизованного админа.
    
    Проверяет JWT токен и возвращает объект Admin.
    
    Raises:
        HTTPException 401: Если токен невалидный или истёк
        HTTPException 401: Если админ не найден
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Невалидный токен авторизации",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Декодируем токен
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise credentials_exception
    
    # Получаем ID админа из токена
    admin_id: int | None = payload.get("sub")
    if admin_id is None:
        raise credentials_exception
    
    # Ищем админа в БД
    result = await db.execute(
        select(Admin).where(Admin.id == int(admin_id))
    )
    admin = result.scalar_one_or_none()
    
    if admin is None:
        raise credentials_exception
    
    return admin


# Типизированные алиасы для использования в роутерах
DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentAdmin = Annotated[Admin, Depends(get_current_admin)]
