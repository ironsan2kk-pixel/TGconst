"""
Загрузка конфигурации бота из главной базы данных (main.db)
"""
from pathlib import Path
from typing import Optional
import aiosqlite

# Путь к главной базе данных
PROJECT_ROOT = Path(__file__).parent.parent.parent
MAIN_DB_PATH = PROJECT_ROOT / "data" / "main.db"


async def load_bot_config(bot_uuid: str) -> Optional[dict]:
    """
    Загрузить конфигурацию бота из main.db по UUID.
    
    Args:
        bot_uuid: UUID бота
        
    Returns:
        Словарь с конфигурацией или None если бот не найден
    """
    if not MAIN_DB_PATH.exists():
        raise FileNotFoundError(f"Главная база данных не найдена: {MAIN_DB_PATH}")
    
    async with aiosqlite.connect(MAIN_DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        cursor = await db.execute(
            """
            SELECT 
                id, uuid, name, bot_token, cryptobot_token,
                welcome_message, support_url, is_active
            FROM bots 
            WHERE uuid = ?
            """,
            (bot_uuid,)
        )
        
        row = await cursor.fetchone()
        
        if not row:
            return None
        
        return {
            "id": row["id"],
            "uuid": row["uuid"],
            "name": row["name"],
            "bot_token": row["bot_token"],
            "cryptobot_token": row["cryptobot_token"],
            "welcome_message": row["welcome_message"] or "👋 Добро пожаловать!",
            "support_url": row["support_url"],
            "is_active": bool(row["is_active"])
        }


async def get_userbot_config() -> Optional[dict]:
    """
    Получить конфигурацию userbot для добавления пользователей.
    
    Returns:
        Словарь с конфигурацией userbot или None
    """
    if not MAIN_DB_PATH.exists():
        return None
    
    async with aiosqlite.connect(MAIN_DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        cursor = await db.execute(
            """
            SELECT api_id, api_hash, phone, session_string, is_active
            FROM userbot_config
            WHERE is_active = 1
            ORDER BY id DESC
            LIMIT 1
            """
        )
        
        row = await cursor.fetchone()
        
        if not row:
            return None
        
        return {
            "api_id": row["api_id"],
            "api_hash": row["api_hash"],
            "phone": row["phone"],
            "session_string": row["session_string"]
        }
