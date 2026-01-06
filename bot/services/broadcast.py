"""
Сервис рассылок.

Поддерживает:
- Создание рассылок с фильтрами
- Отправка с фото и кнопками
- Пауза, отмена, возобновление
- Фоновая отправка
"""

import json
import asyncio
import logging
from datetime import datetime
from typing import Any

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import User, Subscription, Broadcast

logger = logging.getLogger(__name__)


class BroadcastError(Exception):
    """Base broadcast error."""
    pass


class BroadcastNotFoundError(BroadcastError):
    """Broadcast not found."""
    pass


class BroadcastInvalidStateError(BroadcastError):
    """Broadcast is in invalid state for the operation."""
    pass


def parse_buttons(buttons_json: str | None) -> InlineKeyboardMarkup | None:
    """
    Парсинг кнопок из JSON.
    
    Формат JSON:
    [
        [{"text": "Button 1", "url": "https://example.com"}],
        [{"text": "Button 2", "url": "https://example2.com"}]
    ]
    """
    if not buttons_json:
        return None
    
    try:
        data = json.loads(buttons_json)
        if not data:
            return None
        
        rows = []
        for row in data:
            buttons = []
            for btn in row:
                if "url" in btn:
                    buttons.append(InlineKeyboardButton(text=btn["text"], url=btn["url"]))
                elif "callback_data" in btn:
                    buttons.append(InlineKeyboardButton(text=btn["text"], callback_data=btn["callback_data"]))
            if buttons:
                rows.append(buttons)
        
        if rows:
            return InlineKeyboardMarkup(inline_keyboard=rows)
        return None
    except (json.JSONDecodeError, KeyError, TypeError):
        return None


async def get_broadcast_recipients(
    session: AsyncSession,
    filter_type: str = "all",
    filter_language: str = "all",
) -> list[User]:
    """
    Получить список получателей по фильтрам.
    
    Args:
        session: Сессия БД
        filter_type: "all", "active", "inactive", "tariff_X"
        filter_language: "all", "ru", "en"
    
    Returns:
        Список пользователей
    """
    now = datetime.utcnow()
    
    # Базовый запрос - не забаненные юзеры
    stmt = select(User).where(User.is_banned == False)
    
    # Фильтр по языку
    if filter_language != "all":
        stmt = stmt.where(User.language == filter_language)
    
    result = await session.execute(stmt)
    users = result.scalars().all()
    
    # Если нужен фильтр по подпискам
    if filter_type == "all":
        return list(users)
    
    filtered_users = []
    
    for user in users:
        # Проверяем активную подписку
        sub_stmt = select(Subscription).where(
            Subscription.user_id == user.id,
            Subscription.is_active == True,
            (Subscription.expires_at == None) | (Subscription.expires_at > now)
        )
        sub_result = await session.execute(sub_stmt)
        active_sub = sub_result.scalar_one_or_none()
        
        if filter_type == "active":
            if active_sub:
                filtered_users.append(user)
        elif filter_type == "inactive":
            if not active_sub:
                filtered_users.append(user)
        elif filter_type.startswith("tariff_"):
            tariff_id = int(filter_type.split("_")[1])
            if active_sub and active_sub.tariff_id == tariff_id:
                filtered_users.append(user)
    
    return filtered_users


async def count_broadcast_recipients(
    session: AsyncSession,
    filter_type: str = "all",
    filter_language: str = "all",
) -> int:
    """Подсчёт количества получателей."""
    recipients = await get_broadcast_recipients(session, filter_type, filter_language)
    return len(recipients)


async def create_broadcast(
    session: AsyncSession,
    message_text: str,
    message_photo: str | None = None,
    buttons_json: str | None = None,
    filter_type: str = "all",
    filter_language: str = "all",
    scheduled_at: datetime | None = None,
) -> Broadcast:
    """
    Создать новую рассылку.
    
    Args:
        session: Сессия БД
        message_text: Текст сообщения
        message_photo: file_id фото (опционально)
        buttons_json: JSON кнопок (опционально)
        filter_type: Тип фильтра
        filter_language: Фильтр языка
        scheduled_at: Время запланированной отправки
    
    Returns:
        Созданная рассылка
    """
    # Подсчёт получателей
    total_users = await count_broadcast_recipients(session, filter_type, filter_language)
    
    broadcast = Broadcast(
        message_text=message_text,
        message_photo=message_photo,
        buttons_json=buttons_json,
        filter_type=filter_type,
        filter_language=filter_language,
        total_users=total_users,
        status="draft",
        scheduled_at=scheduled_at,
    )
    
    session.add(broadcast)
    await session.commit()
    await session.refresh(broadcast)
    
    logger.info(f"Created broadcast #{broadcast.id} for {total_users} users")
    return broadcast


async def get_broadcast(session: AsyncSession, broadcast_id: int) -> Broadcast:
    """Получить рассылку по ID."""
    broadcast = await session.get(Broadcast, broadcast_id)
    if not broadcast:
        raise BroadcastNotFoundError(f"Broadcast #{broadcast_id} not found")
    return broadcast


async def update_broadcast(
    session: AsyncSession,
    broadcast_id: int,
    **kwargs: Any,
) -> Broadcast:
    """Обновить рассылку."""
    broadcast = await get_broadcast(session, broadcast_id)
    
    if broadcast.status != "draft":
        raise BroadcastInvalidStateError("Can only update draft broadcasts")
    
    for key, value in kwargs.items():
        if hasattr(broadcast, key):
            setattr(broadcast, key, value)
    
    # Пересчитываем получателей если изменились фильтры
    if "filter_type" in kwargs or "filter_language" in kwargs:
        broadcast.total_users = await count_broadcast_recipients(
            session, broadcast.filter_type, broadcast.filter_language
        )
    
    await session.commit()
    await session.refresh(broadcast)
    return broadcast


async def delete_broadcast(session: AsyncSession, broadcast_id: int) -> None:
    """Удалить рассылку."""
    broadcast = await get_broadcast(session, broadcast_id)
    
    if broadcast.status in ("running",):
        raise BroadcastInvalidStateError("Cannot delete running broadcast")
    
    await session.delete(broadcast)
    await session.commit()
    logger.info(f"Deleted broadcast #{broadcast_id}")


async def start_broadcast(
    session: AsyncSession,
    bot: Bot,
    broadcast_id: int,
    delay: float = 0.05,
) -> Broadcast:
    """
    Запустить рассылку.
    
    Args:
        session: Сессия БД
        bot: Telegram Bot
        broadcast_id: ID рассылки
        delay: Задержка между сообщениями (сек)
    
    Returns:
        Обновлённая рассылка
    """
    broadcast = await get_broadcast(session, broadcast_id)
    
    if broadcast.status not in ("draft", "paused"):
        raise BroadcastInvalidStateError(f"Cannot start broadcast in {broadcast.status} state")
    
    # Обновляем статус
    broadcast.status = "running"
    if not broadcast.started_at:
        broadcast.started_at = datetime.utcnow()
    await session.commit()
    
    # Получаем получателей
    recipients = await get_broadcast_recipients(
        session, broadcast.filter_type, broadcast.filter_language
    )
    
    # Парсим кнопки
    keyboard = parse_buttons(broadcast.buttons_json)
    
    # Отправка
    for user in recipients:
        # Проверяем статус (могли поставить на паузу или отменить)
        await session.refresh(broadcast)
        if broadcast.status != "running":
            break
        
        try:
            if broadcast.message_photo:
                await bot.send_photo(
                    user.telegram_id,
                    broadcast.message_photo,
                    caption=broadcast.message_text,
                    reply_markup=keyboard,
                )
            else:
                await bot.send_message(
                    user.telegram_id,
                    broadcast.message_text,
                    reply_markup=keyboard,
                )
            broadcast.sent_count += 1
        except Exception as e:
            logger.warning(f"Failed to send broadcast #{broadcast_id} to user {user.telegram_id}: {e}")
            broadcast.failed_count += 1
        
        await session.commit()
        await asyncio.sleep(delay)
    
    # Завершение
    await session.refresh(broadcast)
    if broadcast.status == "running":
        broadcast.status = "completed"
        broadcast.completed_at = datetime.utcnow()
        await session.commit()
    
    logger.info(
        f"Broadcast #{broadcast_id} finished: sent={broadcast.sent_count}, failed={broadcast.failed_count}"
    )
    
    return broadcast


async def pause_broadcast(session: AsyncSession, broadcast_id: int) -> Broadcast:
    """Поставить рассылку на паузу."""
    broadcast = await get_broadcast(session, broadcast_id)
    
    if broadcast.status != "running":
        raise BroadcastInvalidStateError("Can only pause running broadcasts")
    
    broadcast.status = "paused"
    await session.commit()
    
    logger.info(f"Broadcast #{broadcast_id} paused")
    return broadcast


async def resume_broadcast(
    session: AsyncSession,
    bot: Bot,
    broadcast_id: int,
) -> Broadcast:
    """Возобновить рассылку."""
    broadcast = await get_broadcast(session, broadcast_id)
    
    if broadcast.status != "paused":
        raise BroadcastInvalidStateError("Can only resume paused broadcasts")
    
    # start_broadcast уже поддерживает возобновление
    return await start_broadcast(session, bot, broadcast_id)


async def cancel_broadcast(session: AsyncSession, broadcast_id: int) -> Broadcast:
    """Отменить рассылку."""
    broadcast = await get_broadcast(session, broadcast_id)
    
    if broadcast.status not in ("draft", "running", "paused"):
        raise BroadcastInvalidStateError(f"Cannot cancel broadcast in {broadcast.status} state")
    
    broadcast.status = "cancelled"
    await session.commit()
    
    logger.info(f"Broadcast #{broadcast_id} cancelled")
    return broadcast


async def get_broadcasts_list(
    session: AsyncSession,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[Broadcast]:
    """Получить список рассылок."""
    stmt = select(Broadcast).order_by(Broadcast.created_at.desc())
    
    if status:
        stmt = stmt.where(Broadcast.status == status)
    
    stmt = stmt.limit(limit).offset(offset)
    
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def quick_broadcast(
    session: AsyncSession,
    bot: Bot,
    message_text: str,
    filter_type: str = "all",
    filter_language: str = "all",
) -> dict:
    """
    Быстрая рассылка (синхронная).
    
    Используется для админ-панели в боте.
    
    Returns:
        {"sent": int, "failed": int, "total": int}
    """
    recipients = await get_broadcast_recipients(session, filter_type, filter_language)
    
    sent = 0
    failed = 0
    
    for user in recipients:
        try:
            await bot.send_message(user.telegram_id, message_text)
            sent += 1
        except:
            failed += 1
        await asyncio.sleep(0.05)
    
    return {"sent": sent, "failed": failed, "total": len(recipients)}
