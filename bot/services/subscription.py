"""
Сервис управления подписками.

Создание, активация, деактивация подписок.
"""

from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bot.models import User, Tariff, TariffChannel, Channel, Subscription, Payment


async def create_subscription(
    session: AsyncSession,
    user: User,
    tariff: Tariff,
    payment: Payment | None = None,
    is_trial: bool = False,
    granted_by: int | None = None,
) -> Subscription:
    """
    Создать подписку для пользователя.
    
    Args:
        session: Сессия БД
        user: Пользователь
        tariff: Тариф
        payment: Платёж (если есть)
        is_trial: Пробный период
        granted_by: Telegram ID админа, выдавшего подписку
        
    Returns:
        Созданная подписка
    """
    now = datetime.utcnow()
    
    # Определяем срок действия
    if is_trial and tariff.trial_days > 0:
        duration_days = tariff.trial_days
    elif tariff.duration_days == 0:
        # Навсегда
        duration_days = 0
    else:
        duration_days = tariff.duration_days
    
    # Рассчитываем дату окончания
    expires_at = None
    if duration_days > 0:
        expires_at = now + timedelta(days=duration_days)
    
    # Деактивируем старые подписки на этот же тариф
    stmt = select(Subscription).where(
        Subscription.user_id == user.id,
        Subscription.tariff_id == tariff.id,
        Subscription.is_active == True,
    )
    result = await session.execute(stmt)
    old_subs = result.scalars().all()
    
    for old_sub in old_subs:
        old_sub.is_active = False
    
    # Создаём новую подписку
    subscription = Subscription(
        user_id=user.id,
        tariff_id=tariff.id,
        is_trial=is_trial,
        starts_at=now,
        expires_at=expires_at,
        is_active=True,
        granted_by=granted_by,
    )
    
    session.add(subscription)
    await session.flush()  # Получаем ID
    
    # Связываем с платежом
    if payment:
        payment.subscription_id = subscription.id
    
    await session.commit()
    
    return subscription


async def get_active_subscription(
    session: AsyncSession,
    user_id: int,
    tariff_id: int | None = None,
) -> Subscription | None:
    """
    Получить активную подписку пользователя.
    
    Args:
        session: Сессия БД
        user_id: ID пользователя в БД
        tariff_id: ID тарифа (опционально)
        
    Returns:
        Активная подписка или None
    """
    stmt = select(Subscription).where(
        Subscription.user_id == user_id,
        Subscription.is_active == True,
    ).options(
        selectinload(Subscription.tariff).selectinload(Tariff.tariff_channels).selectinload(TariffChannel.channel)
    )
    
    if tariff_id:
        stmt = stmt.where(Subscription.tariff_id == tariff_id)
    
    result = await session.execute(stmt)
    subscriptions = result.scalars().all()
    
    now = datetime.utcnow()
    
    for sub in subscriptions:
        # Проверяем не истекла ли
        if sub.expires_at is None or sub.expires_at > now:
            return sub
        else:
            # Деактивируем истекшую
            sub.is_active = False
    
    await session.commit()
    return None


async def get_user_subscriptions(
    session: AsyncSession,
    user_id: int,
    active_only: bool = True,
) -> list[Subscription]:
    """
    Получить все подписки пользователя.
    
    Args:
        session: Сессия БД
        user_id: ID пользователя в БД
        active_only: Только активные
        
    Returns:
        Список подписок
    """
    stmt = select(Subscription).where(
        Subscription.user_id == user_id,
    ).options(
        selectinload(Subscription.tariff).selectinload(Tariff.tariff_channels).selectinload(TariffChannel.channel)
    ).order_by(Subscription.created_at.desc())
    
    if active_only:
        stmt = stmt.where(Subscription.is_active == True)
    
    result = await session.execute(stmt)
    subscriptions = result.scalars().all()
    
    if active_only:
        # Фильтруем по дате истечения
        now = datetime.utcnow()
        active_subs = []
        
        for sub in subscriptions:
            if sub.expires_at is None or sub.expires_at > now:
                active_subs.append(sub)
            else:
                sub.is_active = False
        
        await session.commit()
        return active_subs
    
    return list(subscriptions)


async def deactivate_subscription(
    session: AsyncSession,
    subscription: Subscription,
    auto_kicked: bool = False,
) -> None:
    """
    Деактивировать подписку.
    
    Args:
        session: Сессия БД
        subscription: Подписка
        auto_kicked: Был ли автокик
    """
    subscription.is_active = False
    subscription.auto_kicked = auto_kicked
    await session.commit()


async def get_tariff_channels(
    session: AsyncSession,
    tariff: Tariff,
) -> list[Channel]:
    """
    Получить каналы тарифа.
    
    Args:
        session: Сессия БД
        tariff: Тариф
        
    Returns:
        Список каналов
    """
    stmt = select(Channel).join(TariffChannel).where(
        TariffChannel.tariff_id == tariff.id,
        Channel.is_active == True,
    )
    
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def check_user_has_trial(
    session: AsyncSession,
    user_id: int,
    tariff_id: int,
) -> bool:
    """
    Проверить, использовал ли пользователь пробный период для тарифа.
    
    Args:
        session: Сессия БД
        user_id: ID пользователя в БД
        tariff_id: ID тарифа
        
    Returns:
        True если пробный период уже использован
    """
    stmt = select(Subscription).where(
        Subscription.user_id == user_id,
        Subscription.tariff_id == tariff_id,
        Subscription.is_trial == True,
    )
    
    result = await session.execute(stmt)
    return result.scalar_one_or_none() is not None


async def extend_subscription(
    session: AsyncSession,
    subscription: Subscription,
    days: int,
) -> Subscription:
    """
    Продлить подписку на указанное количество дней.
    
    Args:
        session: Сессия БД
        subscription: Подписка
        days: Количество дней
        
    Returns:
        Обновлённая подписка
    """
    if subscription.expires_at is None:
        # Подписка навсегда, ничего не делаем
        return subscription
    
    now = datetime.utcnow()
    
    # Если подписка истекла, продлеваем от текущего момента
    if subscription.expires_at < now:
        subscription.expires_at = now + timedelta(days=days)
    else:
        # Продлеваем от текущей даты окончания
        subscription.expires_at = subscription.expires_at + timedelta(days=days)
    
    subscription.is_active = True
    subscription.notified_3days = False
    subscription.notified_1day = False
    
    await session.commit()
    return subscription
