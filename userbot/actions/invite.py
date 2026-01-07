"""
Действия для добавления пользователей в каналы.
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


async def invite_to_channels(
    user_telegram_id: int,
    channels: list['Channel'],
) -> dict[int, tuple[bool, str]]:
    """
    Добавить пользователя в список каналов.
    
    Args:
        user_telegram_id: Telegram ID пользователя
        channels: Список каналов для добавления
        
    Returns:
        Dict {channel_id: (success, error_message)}
    """
    userbot = await get_userbot()
    results: dict[int, tuple[bool, str]] = {}
    
    for channel in channels:
        if not channel.is_active:
            logger.info(f"Skipping inactive channel {channel.title}")
            continue
        
        success, error = await userbot.invite_user_to_channel(
            channel_id=channel.channel_id,
            user_id=user_telegram_id,
        )
        
        results[channel.channel_id] = (success, error)
        
        if success:
            logger.info(f"User {user_telegram_id} added to {channel.title}")
        else:
            logger.warning(f"Failed to add user {user_telegram_id} to {channel.title}: {error}")
        
        # Задержка между инвайтами
        await asyncio.sleep(userbot_config.INVITE_DELAY)
    
    return results


async def invite_user_to_tariff_channels(
    session: AsyncSession,
    user: 'User',
    tariff: 'Tariff',
) -> dict[int, tuple[bool, str]]:
    """
    Добавить пользователя во все каналы тарифа.
    
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
        Channel.is_active == True,
    )
    result = await session.execute(stmt)
    channels = list(result.scalars().all())
    
    if not channels:
        logger.warning(f"No active channels for tariff {tariff.id}")
        return {}
    
    logger.info(f"Inviting user {user.telegram_id} to {len(channels)} channels for tariff '{tariff.name_ru}'")
    
    return await invite_to_channels(
        user_telegram_id=user.telegram_id,
        channels=channels,
    )


async def invite_user_to_subscription_channels(
    session: AsyncSession,
    subscription: 'Subscription',
) -> dict[int, tuple[bool, str]]:
    """
    Добавить пользователя во все каналы подписки.
    
    Args:
        session: Сессия БД
        subscription: Подписка
        
    Returns:
        Dict {channel_id: (success, error_message)}
    """
    from bot.models import Channel, TariffChannel, User, Tariff
    from sqlalchemy.orm import selectinload
    
    # Загружаем подписку с отношениями если они не загружены
    if not subscription.user or not subscription.tariff:
        stmt = select(type(subscription)).where(
            type(subscription).id == subscription.id
        ).options(
            selectinload(type(subscription).user),
            selectinload(type(subscription).tariff).selectinload(Tariff.tariff_channels).selectinload(TariffChannel.channel),
        )
        result = await session.execute(stmt)
        subscription = result.scalar_one()
    
    return await invite_user_to_tariff_channels(
        session=session,
        user=subscription.user,
        tariff=subscription.tariff,
    )
