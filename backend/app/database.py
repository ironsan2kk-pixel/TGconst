"""
Подключение к базам данных SQLite (async)
"""
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from .config import get_settings


class Base(DeclarativeBase):
    """Базовый класс для всех моделей"""
    pass


# Движки и сессии будут создаваться динамически
_engines: dict = {}
_session_makers: dict = {}


def get_database_url(db_path: Path) -> str:
    """Формирование URL для SQLite"""
    return f"sqlite+aiosqlite:///{db_path.absolute()}"


async def get_main_engine():
    """Получить движок для главной базы данных"""
    settings = get_settings()
    db_path = settings.MAIN_DB_PATH
    
    if "main" not in _engines:
        # Создаём папку если не существует
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        _engines["main"] = create_async_engine(
            get_database_url(db_path),
            echo=settings.DEBUG,
            future=True
        )
    
    return _engines["main"]


async def get_main_session() -> AsyncSession:
    """Получить сессию для главной базы данных"""
    if "main" not in _session_makers:
        engine = await get_main_engine()
        _session_makers["main"] = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async with _session_makers["main"]() as session:
        yield session


async def get_bot_engine(bot_uuid: str):
    """Получить движок для базы данных конкретного бота"""
    settings = get_settings()
    
    if bot_uuid not in _engines:
        db_path = settings.get_bot_db_path(bot_uuid)
        
        # Создаём папку если не существует
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        _engines[bot_uuid] = create_async_engine(
            get_database_url(db_path),
            echo=settings.DEBUG,
            future=True
        )
    
    return _engines[bot_uuid]


async def get_bot_session(bot_uuid: str) -> AsyncSession:
    """Получить сессию для базы данных конкретного бота"""
    if bot_uuid not in _session_makers:
        engine = await get_bot_engine(bot_uuid)
        _session_makers[bot_uuid] = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async with _session_makers[bot_uuid]() as session:
        yield session


async def close_all_engines():
    """Закрыть все соединения (для graceful shutdown)"""
    for engine in _engines.values():
        await engine.dispose()
    _engines.clear()
    _session_makers.clear()
