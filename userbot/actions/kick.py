"""
Действия для удаления пользователей из каналов.
"""

import asyncio
import logging
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

if TYPE_CHECKING:
    from bot.models import User, Channel, Tariff, Subscription

from userbot.config import userbot_config
from userbot.client import get_userbot

logger = logging.getLogger(__name__)


async def kick_from_channels(
    user_telegram_id: int,
    channels: list['Channel'],
) -> dict[int, tuple[bool, str]]:
    """
    Удалить пользователя из списка каналов.
    
    Args:
        user_telegram_id: Telegram ID пользователя
        channels: Список каналов для удаления
        
    Returns:
        Dict {channel_id: (success, error_message)}
    """
    userbot = await get_userbot()
    results: dict[int, tuple[bool, str]] = {}
    
    for channel in channels:
        if not channel.is_active:
            logger.info(f"Skipping inactive channel {channel.title}")
            continue
        
        success, error = await userbot.kick_user_from_channel(
            channel_id=channel.channel_id,
            user_id=user_telegram_id,
        )
        
        results[channel.channel_id] = (success, error)
        
        if success:
            logger.info(f"User {user_telegram_id} kicked from {channel.title}")
        else:
            logger.warning(f"Failed to kick user {user_telegram_id} from {channel.title}: {error}")
        
        # Задержка между киками
        await asyncio.sleep(userbot_config.KICK_DELAY)
    
    return results


async def kick_user_from_tariff_channels(
    session: AsyncSession,
    user: 'User',
    tariff: 'Tariff',
) -> dict[int, tuple[bool, str]]:
    """
    Удалить пользователя из всех каналов тарифа.
    
    Args:
        session: Сессия БД
        user: Пользователь
        tariff: Тариф
        
    Returns:
        Dict {channel_id: (success, error_message)}
    """
    from bot.models import Channel, TariffChannel
    
    # Получаем каналы тарифа
    stmt = select(Channel).join(TariffChannel).where(
        TariffChannel.tariff_id == tariff.id,
    )
    result = await session.execute(stmt)
    channels = list(result.scalars().all())
    
    if not channels:
        logger.warning(f"No channels for tariff {tariff.id}")
        return {}
    
    logger.info(f"Kicking user {user.telegram_id} from {len(channels)} channels")
    
    return await kick_from_channels(
        user_telegram_id=user.telegram_id,
        channels=channels,
    )


async def kick_user_from_subscription_channels(
    session: AsyncSession,
    subscription: 'Subscription',
) -> dict[int, tuple[bool, str]]:
    """
    Удалить пользователя из всех каналов подписки.
    
    Args:
        session: Сессия БД
        subscription: Подписка
        
    Returns:
        Dict {channel_id: (success, error_message)}
    """
    from bot.models import Channel, TariffChannel, User, Tariff, Subscription
    from sqlalchemy.orm import selectinload
    
    # Загружаем подписку с отношениями если они не загружены
    if not subscription.user or not subscription.tariff:
        stmt = select(Subscription).where(
            Subscription.id == subscription.id
        ).options(
            selectinload(Subscription.user),
            selectinload(Subscription.tariff).selectinload(Tariff.tariff_channels).selectinload(TariffChannel.channel),
        )
        result = await session.execute(stmt)
        subscription = result.scalar_one()
    
    return await kick_user_from_tariff_channels(
        session=session,
        user=subscription.user,
        tariff=subscription.tariff,
    )


async def kick_user_from_all_channels(
    session: AsyncSession,
    user: 'User',
) -> dict[int, tuple[bool, str]]:
    """
    Удалить пользователя из ВСЕХ каналов (при бане например).
    
    Args:
        session: Сессия БД
        user: Пользователь
        
    Returns:
        Dict {channel_id: (success, error_message)}
    """
    from bot.models import Channel
    
    # Получаем все активные каналы
    stmt = select(Channel).where(Channel.is_active == True)
    result = await session.execute(stmt)
    channels = list(result.scalars().all())
    
    if not channels:
        return {}
    
    logger.info(f"Kicking user {user.telegram_id} from ALL {len(channels)} channels")
    
    return await kick_from_channels(
        user_telegram_id=user.telegram_id,
        channels=channels,
    )
