"""
Действие: Удаление пользователя из канала (кик)
"""

import asyncio
import logging
from typing import Optional
from datetime import datetime
import aiosqlite

from ..client import get_userbot_client
from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


async def kick_user_from_channel(
    user_telegram_id: int,
    channel_id: int,
    max_retries: int = 3
) -> dict:
    """
    Удалить пользователя из канала с повторными попытками
    
    Args:
        user_telegram_id: Telegram ID пользователя
        channel_id: Telegram ID канала
        max_retries: Максимум попыток при FloodWait
    
    Returns:
        {
            "success": bool,
            "error": str или None,
            "attempts": int
        }
    """
    client = get_userbot_client()
    
    if not client.is_connected:
        logger.error("Userbot не подключен")
        return {
            "success": False,
            "error": "Userbot не подключен",
            "attempts": 0
        }
    
    attempts = 0
    last_error = None
    
    while attempts < max_retries:
        attempts += 1
        
        result = await client.kick_user_from_channel(
            user_id=user_telegram_id,
            channel_id=channel_id
        )
        
        if result["success"]:
            return {
                "success": True,
                "error": None,
                "attempts": attempts
            }
        
        # Если FloodWait - ждём и пробуем ещё раз
        if result.get("error_type") == "flood_wait":
            # Парсим время ожидания из ошибки
            import re
            match = re.search(r'(\d+)', result.get("error", ""))
            if match:
                wait_time = int(int(match.group(1)) * settings.FLOOD_WAIT_MULTIPLIER)
                logger.info(f"FloodWait: ждём {wait_time} секунд (попытка {attempts}/{max_retries})")
                await asyncio.sleep(wait_time)
                continue
        
        # Другие ошибки - не повторяем
        last_error = result["error"]
        break
    
    return {
        "success": False,
        "error": last_error or "Превышено количество попыток",
        "attempts": attempts
    }


async def process_kick_task(
    bot_uuid: str,
    user_telegram_id: int,
    channel_id: int,
    subscription_id: int,
    send_notification: bool = True
) -> dict:
    """
    Обработать задачу на удаление пользователя из канала
    
    Эта функция:
    1. Удаляет пользователя из канала
    2. Обновляет статус подписки в БД бота
    3. Опционально отправляет уведомление пользователю
    
    Args:
        bot_uuid: UUID бота
        user_telegram_id: Telegram ID пользователя
        channel_id: ID канала в БД (не telegram_id)
        subscription_id: ID подписки
        send_notification: Отправить уведомление пользователю
    
    Returns:
        dict с результатом
    """
    logger.info(
        f"Обработка кика: user={user_telegram_id}, "
        f"channel={channel_id}, subscription={subscription_id}, bot={bot_uuid}"
    )
    
    # Получаем реальный channel_id из БД бота
    bot_db_path = settings.get_bot_db_path(bot_uuid)
    
    if not bot_db_path.exists():
        logger.error(f"БД бота не найдена: {bot_db_path}")
        return {
            "success": False,
            "error": "БД бота не найдена"
        }
    
    telegram_channel_id = None
    channel_title = None
    
    try:
        async with aiosqlite.connect(bot_db_path) as db:
            # Получаем telegram_channel_id из таблицы channels
            cursor = await db.execute(
                "SELECT channel_id, title FROM channels WHERE id = ?",
                (channel_id,)
            )
            row = await cursor.fetchone()
            
            if not row:
                logger.error(f"Канал не найден: {channel_id}")
                return {
                    "success": False,
                    "error": "Канал не найден в БД"
                }
            
            telegram_channel_id = row[0]
            channel_title = row[1]
    
    except Exception as e:
        logger.exception(f"Ошибка чтения БД: {e}")
        return {
            "success": False,
            "error": f"Ошибка БД: {e}"
        }
    
    # Удаляем пользователя из канала
    result = await kick_user_from_channel(
        user_telegram_id=user_telegram_id,
        channel_id=telegram_channel_id,
        max_retries=settings.INVITE_MAX_RETRIES
    )
    
    if result["success"]:
        logger.info(
            f"✅ Пользователь {user_telegram_id} удалён из канала {telegram_channel_id} "
            f"(попыток: {result['attempts']})"
        )
        
        # Обновляем статус подписки
        try:
            async with aiosqlite.connect(bot_db_path) as db:
                await db.execute(
                    """
                    UPDATE subscriptions 
                    SET is_active = 0, auto_kicked = 1 
                    WHERE id = ?
                    """,
                    (subscription_id,)
                )
                await db.commit()
                logger.info(f"Подписка {subscription_id} помечена как неактивная")
        except Exception as e:
            logger.error(f"Ошибка обновления подписки: {e}")
    else:
        logger.error(
            f"❌ Не удалось удалить {user_telegram_id} из канала {telegram_channel_id}: "
            f"{result['error']}"
        )
    
    return result


async def batch_kick_expired_subscriptions(bot_uuid: str) -> dict:
    """
    Массовое удаление пользователей с истёкшими подписками
    
    Args:
        bot_uuid: UUID бота
    
    Returns:
        {
            "processed": int,
            "success": int,
            "failed": int,
            "errors": list
        }
    """
    bot_db_path = settings.get_bot_db_path(bot_uuid)
    
    if not bot_db_path.exists():
        logger.error(f"БД бота не найдена: {bot_db_path}")
        return {
            "processed": 0,
            "success": 0,
            "failed": 0,
            "errors": ["БД бота не найдена"]
        }
    
    expired_subscriptions = []
    
    try:
        async with aiosqlite.connect(bot_db_path) as db:
            db.row_factory = aiosqlite.Row
            
            # Находим все истёкшие активные подписки
            cursor = await db.execute(
                """
                SELECT 
                    s.id as subscription_id,
                    s.channel_id,
                    u.telegram_id as user_telegram_id,
                    c.channel_id as telegram_channel_id
                FROM subscriptions s
                JOIN users u ON s.user_id = u.id
                JOIN channels c ON s.channel_id = c.id
                WHERE s.is_active = 1 
                  AND s.auto_kicked = 0
                  AND s.expires_at < datetime('now')
                """
            )
            
            rows = await cursor.fetchall()
            expired_subscriptions = [dict(row) for row in rows]
    
    except Exception as e:
        logger.exception(f"Ошибка чтения истёкших подписок: {e}")
        return {
            "processed": 0,
            "success": 0,
            "failed": 0,
            "errors": [str(e)]
        }
    
    if not expired_subscriptions:
        logger.info(f"Нет истёкших подписок для бота {bot_uuid}")
        return {
            "processed": 0,
            "success": 0,
            "failed": 0,
            "errors": []
        }
    
    logger.info(f"Найдено {len(expired_subscriptions)} истёкших подписок для бота {bot_uuid}")
    
    success_count = 0
    failed_count = 0
    errors = []
    
    for sub in expired_subscriptions:
        result = await process_kick_task(
            bot_uuid=bot_uuid,
            user_telegram_id=sub["user_telegram_id"],
            channel_id=sub["channel_id"],
            subscription_id=sub["subscription_id"],
            send_notification=True
        )
        
        if result["success"]:
            success_count += 1
        else:
            failed_count += 1
            errors.append(f"User {sub['user_telegram_id']}: {result.get('error')}")
        
        # Небольшая задержка между операциями чтобы не получить FloodWait
        await asyncio.sleep(1)
    
    return {
        "processed": len(expired_subscriptions),
        "success": success_count,
        "failed": failed_count,
        "errors": errors
    }
