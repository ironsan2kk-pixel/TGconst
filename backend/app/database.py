"""
Подключение к базам данных SQLite (async)
"""
from pathlib import Path
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from .config import get_settings


class MainBase(DeclarativeBase):
    """Базовый класс для моделей главной БД (main.db)"""
    pass


class BotBase(DeclarativeBase):
    """Базовый класс для моделей БД бота (bot.db)"""
    pass


# Для обратной совместимости
Base = MainBase


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
    """Получить сессию для главной базы данных (прямой вызов, не dependency)"""
    if "main" not in _session_makers:
        engine = await get_main_engine()
        _session_makers["main"] = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    return _session_makers["main"]()


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


async def init_main_db():
    """
    Инициализация главной базы данных.
    Создаёт все таблицы если они не существуют.
    """
    from .models.main_db import Admin, Bot, UserbotConfig
    
    engine = await get_main_engine()
    
    async with engine.begin() as conn:
        # Создаём таблицы для главной БД
        await conn.run_sync(MainBase.metadata.create_all)
    
    return engine


async def init_bot_db(bot_uuid: str):
    """
    Инициализация базы данных конкретного бота.
    Создаёт папку и все таблицы если они не существуют.
    
    Args:
        bot_uuid: UUID бота
    """
    from .models.bot_db import (
        Channel, Tariff, User, Subscription, 
        Payment, Promocode, Broadcast
    )
    
    settings = get_settings()
    bot_dir = settings.get_bot_dir(bot_uuid)
    
    # Создаём папку для бота
    bot_dir.mkdir(parents=True, exist_ok=True)
    
    # Создаём папку для логов
    logs_dir = bot_dir / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    engine = await get_bot_engine(bot_uuid)
    
    async with engine.begin() as conn:
        # Создаём таблицы для БД бота
        await conn.run_sync(BotBase.metadata.create_all)
    
    return engine


async def delete_bot_db(bot_uuid: str):
    """
    Удаление базы данных бота и его папки.
    
    Args:
        bot_uuid: UUID бота
    """
    import shutil
    
    settings = get_settings()
    bot_dir = settings.get_bot_dir(bot_uuid)
    
    # Закрываем соединение если открыто
    if bot_uuid in _engines:
        await _engines[bot_uuid].dispose()
        del _engines[bot_uuid]
    
    if bot_uuid in _session_makers:
        del _session_makers[bot_uuid]
    
    # Удаляем папку с БД
    if bot_dir.exists():
        shutil.rmtree(bot_dir)


async def get_main_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency для FastAPI - получение сессии главной БД.
    Использовать в роутах: db: AsyncSession = Depends(get_main_db)
    """
    if "main" not in _session_makers:
        engine = await get_main_engine()
        _session_makers["main"] = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async with _session_makers["main"]() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_bot_db(bot_uuid: str) -> AsyncGenerator[AsyncSession, None]:
    """
    Получение сессии БД конкретного бота.
    
    Args:
        bot_uuid: UUID бота
    """
    if bot_uuid not in _session_makers:
        engine = await get_bot_engine(bot_uuid)
        _session_makers[bot_uuid] = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async with _session_makers[bot_uuid]() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
