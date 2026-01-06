"""
Подключение к базе данных бота (bot.db)
"""
from pathlib import Path
from typing import Optional, List
from datetime import datetime
import aiosqlite

# Путь к папке с данными
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "bots"

# Глобальное соединение
_db_connection: Optional[aiosqlite.Connection] = None
_bot_uuid: Optional[str] = None


def get_db_path(bot_uuid: str) -> Path:
    """Получить путь к базе данных бота"""
    return DATA_DIR / bot_uuid / "bot.db"


async def init_database(bot_uuid: str):
    """
    Инициализация подключения к базе данных бота.
    
    Args:
        bot_uuid: UUID бота
    """
    global _db_connection, _bot_uuid
    
    db_path = get_db_path(bot_uuid)
    
    if not db_path.exists():
        raise FileNotFoundError(f"База данных бота не найдена: {db_path}")
    
    _db_connection = await aiosqlite.connect(db_path)
    _db_connection.row_factory = aiosqlite.Row
    _bot_uuid = bot_uuid


async def get_db() -> aiosqlite.Connection:
    """Получить соединение с базой данных"""
    if _db_connection is None:
        raise RuntimeError("База данных не инициализирована. Вызовите init_database()")
    return _db_connection


async def close_database():
    """Закрыть соединение с базой данных"""
    global _db_connection
    if _db_connection:
        await _db_connection.close()
        _db_connection = None


# ============ USERS ============

async def get_or_create_user(
    telegram_id: int,
    username: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None
) -> dict:
    """
    Получить или создать пользователя.
    
    Args:
        telegram_id: Telegram ID пользователя
        username: @username
        first_name: Имя
        last_name: Фамилия
        
    Returns:
        Словарь с данными пользователя
    """
    db = await get_db()
    
    # Проверяем существует ли пользователь
    cursor = await db.execute(
        "SELECT * FROM users WHERE telegram_id = ?",
        (telegram_id,)
    )
    row = await cursor.fetchone()
    
    if row:
        # Обновляем данные пользователя если изменились
        await db.execute(
            """
            UPDATE users 
            SET username = ?, first_name = ?, last_name = ?, last_activity = ?
            WHERE telegram_id = ?
            """,
            (username, first_name, last_name, datetime.utcnow().isoformat(), telegram_id)
        )
        await db.commit()
        
        # Получаем обновленные данные
        cursor = await db.execute(
            "SELECT * FROM users WHERE telegram_id = ?",
            (telegram_id,)
        )
        row = await cursor.fetchone()
    else:
        # Создаём нового пользователя
        now = datetime.utcnow().isoformat()
        await db.execute(
            """
            INSERT INTO users (telegram_id, username, first_name, last_name, is_blocked, created_at, last_activity)
            VALUES (?, ?, ?, ?, 0, ?, ?)
            """,
            (telegram_id, username, first_name, last_name, now, now)
        )
        await db.commit()
        
        cursor = await db.execute(
            "SELECT * FROM users WHERE telegram_id = ?",
            (telegram_id,)
        )
        row = await cursor.fetchone()
    
    return dict(row)


async def get_user_by_telegram_id(telegram_id: int) -> Optional[dict]:
    """Получить пользователя по Telegram ID"""
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM users WHERE telegram_id = ?",
        (telegram_id,)
    )
    row = await cursor.fetchone()
    return dict(row) if row else None


# ============ CHANNELS ============

async def get_active_channels() -> List[dict]:
    """Получить список активных каналов"""
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM channels WHERE is_active = 1 ORDER BY id"
    )
    rows = await cursor.fetchall()
    return [dict(row) for row in rows]


async def get_channel_by_id(channel_id: int) -> Optional[dict]:
    """Получить канал по ID"""
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM channels WHERE id = ?",
        (channel_id,)
    )
    row = await cursor.fetchone()
    return dict(row) if row else None


# ============ TARIFFS ============

async def get_tariffs_by_channel(channel_id: int) -> List[dict]:
    """Получить тарифы канала"""
    db = await get_db()
    cursor = await db.execute(
        """
        SELECT * FROM tariffs 
        WHERE channel_id = ? AND is_active = 1
        ORDER BY sort_order, price
        """,
        (channel_id,)
    )
    rows = await cursor.fetchall()
    return [dict(row) for row in rows]


async def get_tariff_by_id(tariff_id: int) -> Optional[dict]:
    """Получить тариф по ID"""
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM tariffs WHERE id = ?",
        (tariff_id,)
    )
    row = await cursor.fetchone()
    return dict(row) if row else None


# ============ SUBSCRIPTIONS ============

async def get_user_subscriptions(user_id: int, active_only: bool = True) -> List[dict]:
    """
    Получить подписки пользователя.
    
    Args:
        user_id: ID пользователя в базе
        active_only: Только активные подписки
    """
    db = await get_db()
    
    query = """
        SELECT s.*, c.title as channel_title, c.channel_username
        FROM subscriptions s
        JOIN channels c ON s.channel_id = c.id
        WHERE s.user_id = ?
    """
    
    if active_only:
        query += " AND s.is_active = 1"
    
    query += " ORDER BY s.expires_at DESC"
    
    cursor = await db.execute(query, (user_id,))
    rows = await cursor.fetchall()
    return [dict(row) for row in rows]


async def get_active_subscription(user_id: int, channel_id: int) -> Optional[dict]:
    """Получить активную подписку пользователя на канал"""
    db = await get_db()
    cursor = await db.execute(
        """
        SELECT * FROM subscriptions 
        WHERE user_id = ? AND channel_id = ? AND is_active = 1
        ORDER BY expires_at DESC
        LIMIT 1
        """,
        (user_id, channel_id)
    )
    row = await cursor.fetchone()
    return dict(row) if row else None


# ============ PAYMENTS ============

async def create_payment(
    user_id: int,
    invoice_id: str,
    amount: float,
    currency: str,
    tariff_id: int,
    channel_id: int,
    promocode_id: Optional[int] = None,
    discount_amount: float = 0.0
) -> int:
    """
    Создать запись о платеже.
    
    Returns:
        ID созданного платежа
    """
    db = await get_db()
    now = datetime.utcnow().isoformat()
    
    cursor = await db.execute(
        """
        INSERT INTO payments (
            user_id, invoice_id, amount, currency, status,
            tariff_id, channel_id, promocode_id, discount_amount, created_at
        )
        VALUES (?, ?, ?, ?, 'pending', ?, ?, ?, ?, ?)
        """,
        (user_id, invoice_id, amount, currency, tariff_id, channel_id, promocode_id, discount_amount, now)
    )
    await db.commit()
    
    return cursor.lastrowid


async def get_pending_payment(user_id: int, tariff_id: int) -> Optional[dict]:
    """Получить незавершенный платеж пользователя за тариф"""
    db = await get_db()
    cursor = await db.execute(
        """
        SELECT * FROM payments 
        WHERE user_id = ? AND tariff_id = ? AND status = 'pending'
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (user_id, tariff_id)
    )
    row = await cursor.fetchone()
    return dict(row) if row else None


# ============ PROMOCODES ============

async def get_promocode_by_code(code: str) -> Optional[dict]:
    """Получить промокод по коду"""
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM promocodes WHERE code = ? AND is_active = 1",
        (code.upper(),)
    )
    row = await cursor.fetchone()
    return dict(row) if row else None


async def validate_promocode(code: str) -> tuple[bool, Optional[dict], str]:
    """
    Валидация промокода.
    
    Returns:
        (is_valid, promocode_data, error_message)
    """
    promo = await get_promocode_by_code(code)
    
    if not promo:
        return False, None, "❌ Промокод не найден"
    
    now = datetime.utcnow()
    
    # Проверяем срок действия
    if promo["valid_from"]:
        valid_from = datetime.fromisoformat(promo["valid_from"])
        if now < valid_from:
            return False, None, "❌ Промокод ещё не активен"
    
    if promo["valid_until"]:
        valid_until = datetime.fromisoformat(promo["valid_until"])
        if now > valid_until:
            return False, None, "❌ Срок действия промокода истёк"
    
    # Проверяем лимит использований
    if promo["max_uses"] is not None:
        if promo["used_count"] >= promo["max_uses"]:
            return False, None, "❌ Лимит использований промокода исчерпан"
    
    return True, promo, ""


async def use_promocode(promocode_id: int):
    """Увеличить счётчик использований промокода"""
    db = await get_db()
    await db.execute(
        "UPDATE promocodes SET used_count = used_count + 1 WHERE id = ?",
        (promocode_id,)
    )
    await db.commit()
