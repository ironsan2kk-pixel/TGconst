"""
Действие: Добавление пользователя в канал
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


async def invite_user_to_channel(
    user_telegram_id: int,
    channel_id: int,
    max_retries: int = 3
) -> dict:
    """
    Добавить пользователя в канал с повторными попытками
    
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
        
        result = await client.invite_user_to_channel(
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
        if result["error_type"] == "flood_wait" and result["retry_after"]:
            wait_time = int(result["retry_after"] * settings.FLOOD_WAIT_MULTIPLIER)
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


async def process_invite_task(
    bot_uuid: str,
    user_telegram_id: int,
    channel_id: int,
    subscription_id: int
) -> dict:
    """
    Обработать задачу на добавление пользователя
    
    Эта функция:
    1. Добавляет пользователя в канал
    2. Обновляет статус в БД бота
    3. Логирует результат
    
    Args:
        bot_uuid: UUID бота
        user_telegram_id: Telegram ID пользователя
        channel_id: Telegram ID канала (из таблицы channels)
        subscription_id: ID подписки
    
    Returns:
        dict с результатом
    """
    logger.info(
        f"Обработка задачи: user={user_telegram_id}, "
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
    
    try:
        async with aiosqlite.connect(bot_db_path) as db:
            # Получаем telegram_channel_id из таблицы channels
            cursor = await db.execute(
                "SELECT channel_id FROM channels WHERE id = ?",
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
    
    except Exception as e:
        logger.exception(f"Ошибка чтения БД: {e}")
        return {
            "success": False,
            "error": f"Ошибка БД: {e}"
        }
    
    # Добавляем пользователя
    result = await invite_user_to_channel(
        user_telegram_id=user_telegram_id,
        channel_id=telegram_channel_id,
        max_retries=settings.INVITE_MAX_RETRIES
    )
    
    # Логируем результат
    if result["success"]:
        logger.info(
            f"✅ Пользователь {user_telegram_id} добавлен в канал {telegram_channel_id} "
            f"(попыток: {result['attempts']})"
        )
    else:
        logger.error(
            f"❌ Не удалось добавить {user_telegram_id} в канал {telegram_channel_id}: "
            f"{result['error']}"
        )
    
    return result


async def kick_user_from_channel_task(
    bot_uuid: str,
    user_telegram_id: int,
    channel_id: int,
    subscription_id: int
) -> dict:
    """
    Обработать задачу на удаление пользователя из канала
    
    Args:
        bot_uuid: UUID бота
        user_telegram_id: Telegram ID пользователя
        channel_id: ID канала в БД
        subscription_id: ID подписки
    
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
    
    try:
        async with aiosqlite.connect(bot_db_path) as db:
            cursor = await db.execute(
                "SELECT channel_id FROM channels WHERE id = ?",
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
    
    except Exception as e:
        logger.exception(f"Ошибка чтения БД: {e}")
        return {
            "success": False,
            "error": f"Ошибка БД: {e}"
        }
    
    # Удаляем пользователя
    client = get_userbot_client()
    
    if not client.is_connected:
        logger.error("Userbot не подключен")
        return {
            "success": False,
            "error": "Userbot не подключен"
        }
    
    result = await client.kick_user_from_channel(
        user_id=user_telegram_id,
        channel_id=telegram_channel_id
    )
    
    if result["success"]:
        logger.info(f"✅ Пользователь {user_telegram_id} удалён из канала {telegram_channel_id}")
        
        # Обновляем статус подписки
        try:
            async with aiosqlite.connect(bot_db_path) as db:
                await db.execute(
                    "UPDATE subscriptions SET is_active = 0, auto_kicked = 1 WHERE id = ?",
                    (subscription_id,)
                )
                await db.commit()
        except Exception as e:
            logger.error(f"Ошибка обновления подписки: {e}")
    else:
        logger.error(
            f"❌ Не удалось удалить {user_telegram_id} из канала {telegram_channel_id}: "
            f"{result['error']}"
        )
    
    return result
