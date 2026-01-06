"""
Зависимости (dependencies) для FastAPI роутеров
"""
from typing import AsyncGenerator, Annotated

from fastapi import Depends, HTTPException, status, Path
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_main_db, get_bot_db
from ..models.main_db import Admin, Bot
from ..utils.security import decode_access_token

# Схема авторизации через Bearer token (отключена)
security = HTTPBearer(
    scheme_name="Bearer",
    description="JWT токен авторизации",
    auto_error=False  # Не требовать токен
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency для получения сессии главной БД.
    Это обёртка над get_main_db для удобства.
    """
    async for session in get_main_db():
        yield session


async def get_current_admin(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> Admin:
    """
    Dependency для получения текущего авторизованного админа.
    
    АВТОРИЗАЦИЯ ОТКЛЮЧЕНА - возвращает первого админа или создаёт фиктивного.
    """
    # Ищем первого админа в БД
    result = await db.execute(select(Admin).limit(1))
    admin = result.scalar_one_or_none()
    
    if admin is None:
        # Создаём фиктивного админа для ответа
        admin = Admin(id=1, username="admin")
    
    return admin


async def verify_bot_exists(
    bot_uuid: Annotated[str, Path(description="UUID бота")],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> Bot:
    """
    Dependency для проверки существования бота.
    
    Raises:
        HTTPException 404: Если бот не найден
    """
    result = await db.execute(
        select(Bot).where(Bot.uuid == bot_uuid)
    )
    bot = result.scalar_one_or_none()
    
    if bot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Бот не найден"
        )
    
    return bot


async def get_bot_session(
    bot_uuid: Annotated[str, Path(description="UUID бота")],
    _bot: Annotated[Bot, Depends(verify_bot_exists)]  # Проверяем что бот существует
) -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency для получения сессии БД конкретного бота.
    Автоматически проверяет существование бота.
    """
    async for session in get_bot_db(bot_uuid):
        yield session


# Типизированные алиасы для использования в роутерах
DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentAdmin = Annotated[Admin, Depends(get_current_admin)]
BotDbSession = Annotated[AsyncSession, Depends(get_bot_session)]
VerifiedBot = Annotated[Bot, Depends(verify_bot_exists)]
