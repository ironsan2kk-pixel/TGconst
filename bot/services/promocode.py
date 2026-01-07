"""
Сервис управления промокодами.

Проверка, применение, учёт использования.
"""

from datetime import datetime
from typing import Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import User, Promocode, PromocodeUse, Tariff


class PromocodeError(Exception):
    """Базовая ошибка промокода."""
    pass


class PromocodeNotFoundError(PromocodeError):
    """Промокод не найден."""
    pass


class PromocodeExpiredError(PromocodeError):
    """Промокод истёк."""
    pass


class PromocodeAlreadyUsedError(PromocodeError):
    """Промокод уже использован."""
    pass


class PromocodeLimitReachedError(PromocodeError):
    """Лимит использований исчерпан."""
    pass


class PromocodeNotApplicableError(PromocodeError):
    """Промокод не применим к тарифу."""
    pass


async def get_promocode(
    session: AsyncSession,
    code: str,
) -> Promocode | None:
    """
    Получить промокод по коду.
    
    Args:
        session: Сессия БД
        code: Код промокода
        
    Returns:
        Промокод или None
    """
    stmt = select(Promocode).where(
        Promocode.code == code.upper().strip()
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def validate_promocode(
    session: AsyncSession,
    code: str,
    user: User,
    tariff: Tariff | None = None,
) -> Tuple[Promocode, float]:
    """
    Проверить и получить скидку по промокоду.
    
    Args:
        session: Сессия БД
        code: Код промокода
        user: Пользователь
        tariff: Тариф (опционально, для проверки применимости)
        
    Returns:
        Tuple[Promocode, discount_amount]
        
    Raises:
        PromocodeNotFoundError: Промокод не найден
        PromocodeExpiredError: Промокод истёк
        PromocodeAlreadyUsedError: Уже использован этим юзером
        PromocodeLimitReachedError: Лимит исчерпан
        PromocodeNotApplicableError: Не применим к тарифу
    """
    promo = await get_promocode(session, code)
    
    if not promo:
        raise PromocodeNotFoundError("Промокод не найден")
    
    if not promo.is_active:
        raise PromocodeNotFoundError("Промокод неактивен")
    
    now = datetime.utcnow()
    
    # Проверяем даты действия
    if promo.valid_from and now < promo.valid_from:
        raise PromocodeNotFoundError("Промокод ещё не активен")
    
    if promo.valid_until and now > promo.valid_until:
        raise PromocodeExpiredError("Промокод истёк")
    
    # Проверяем лимит использований
    if promo.max_uses is not None and promo.used_count >= promo.max_uses:
        raise PromocodeLimitReachedError("Лимит использований исчерпан")
    
    # Проверяем, использовал ли этот юзер уже этот промокод
    stmt = select(PromocodeUse).where(
        PromocodeUse.promocode_id == promo.id,
        PromocodeUse.user_id == user.id,
    )
    result = await session.execute(stmt)
    if result.scalar_one_or_none():
        raise PromocodeAlreadyUsedError("Вы уже использовали этот промокод")
    
    # Проверяем применимость к тарифу
    if tariff and promo.tariff_id and promo.tariff_id != tariff.id:
        raise PromocodeNotApplicableError("Промокод не применим к этому тарифу")
    
    # Рассчитываем скидку
    if tariff:
        original_price = tariff.price
        discounted_price = promo.calculate_discount(original_price)
        discount = original_price - discounted_price
    else:
        discount = 0.0
        if promo.discount_amount > 0:
            discount = promo.discount_amount
        elif promo.discount_percent > 0:
            discount = promo.discount_percent  # Вернём процент
    
    return promo, discount


async def apply_promocode(
    session: AsyncSession,
    promocode: Promocode,
    user: User,
    payment_id: int | None = None,
) -> PromocodeUse:
    """
    Применить промокод (записать использование).
    
    Args:
        session: Сессия БД
        promocode: Промокод
        user: Пользователь
        payment_id: ID платежа (опционально)
        
    Returns:
        Запись использования
    """
    # Создаём запись использования
    use = PromocodeUse(
        promocode_id=promocode.id,
        user_id=user.id,
        payment_id=payment_id,
    )
    
    session.add(use)
    
    # Увеличиваем счётчик
    promocode.used_count += 1
    
    await session.commit()
    
    return use


async def get_user_active_promocode(
    session: AsyncSession,
    user_id: int,
) -> Promocode | None:
    """
    Получить активный применённый промокод юзера (если есть неиспользованный в платеже).
    
    Это для случая, когда юзер ввёл промокод, но ещё не оплатил.
    """
    # В этой реализации промокод сразу привязывается к платежу
    # Здесь можно добавить логику хранения "активного" промокода в сессии FSM
    return None


def format_discount(promocode: Promocode) -> str:
    """Форматировать скидку для отображения."""
    if promocode.discount_percent > 0:
        return f"{promocode.discount_percent}%"
    elif promocode.discount_amount > 0:
        return f"{promocode.discount_amount:.2f} USDT"
    return "0"
