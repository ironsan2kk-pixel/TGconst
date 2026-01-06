#!/usr/bin/env python3
"""
Скрипт создания первого администратора.

Использование:
    python scripts/create_admin.py
    python scripts/create_admin.py --username admin --password secret123
"""
import sys
import asyncio
import argparse
from pathlib import Path

# Добавляем backend в path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from passlib.context import CryptContext
from sqlalchemy import select
from app.config import get_settings
from app.database import init_main_db, get_main_engine, Base
from app.models.main_db import Admin, Bot, UserbotConfig

# Контекст для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Хеширование пароля"""
    return pwd_context.hash(password)


async def create_admin(username: str, password: str) -> bool:
    """
    Создание администратора в базе данных.
    
    Args:
        username: Логин
        password: Пароль
        
    Returns:
        True если админ создан, False если уже существует
    """
    from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
    
    settings = get_settings()
    
    print(f"📁 Папка данных: {settings.DATA_DIR}")
    print(f"📄 Путь к main.db: {settings.MAIN_DB_PATH}")
    
    # Создаём папку data если не существует
    settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
    settings.bots_dir.mkdir(parents=True, exist_ok=True)
    
    # Инициализируем БД (создаём таблицы)
    engine = await get_main_engine()
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Таблицы созданы")
    
    # Создаём сессию
    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with session_maker() as session:
        # Проверяем существует ли уже админ
        result = await session.execute(
            select(Admin).where(Admin.username == username)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            print(f"⚠️  Администратор '{username}' уже существует")
            return False
        
        # Создаём нового админа
        admin = Admin(
            username=username,
            password_hash=hash_password(password)
        )
        session.add(admin)
        await session.commit()
        
        print(f"✅ Администратор создан:")
        print(f"   Логин: {username}")
        print(f"   Пароль: {password}")
        
        return True


async def main():
    parser = argparse.ArgumentParser(description="Создание администратора")
    parser.add_argument(
        "--username", "-u",
        help="Имя пользователя (по умолчанию из .env)"
    )
    parser.add_argument(
        "--password", "-p", 
        help="Пароль (по умолчанию из .env)"
    )
    
    args = parser.parse_args()
    
    settings = get_settings()
    
    username = args.username or settings.ADMIN_USERNAME
    password = args.password or settings.ADMIN_PASSWORD
    
    print("=" * 50)
    print("🔧 Создание администратора")
    print("=" * 50)
    
    try:
        await create_admin(username, password)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        sys.exit(1)
    
    print("=" * 50)
    print("✅ Готово!")


if __name__ == "__main__":
    asyncio.run(main())
