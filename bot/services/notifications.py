"""
Сервис уведомлений для админов.
"""

import logging
from aiogram import Bot

from bot.config import config
from bot.models import User
from bot.locales import get_text

logger = logging.getLogger(__name__)


async def notify_admins(bot: Bot, text: str) -> None:
    """
    Отправить уведомление всем админам.
    
    Args:
        bot: Экземпляр бота
        text: Текст уведомления
    """
    for admin_id in config.ADMIN_IDS:
        try:
            await bot.send_message(admin_id, text)
        except Exception as e:
            logger.error(f"Failed to notify admin {admin_id}: {e}")


async def notify_new_user(bot: Bot, user: User) -> None:
    """
    Уведомить админов о новом пользователе.
    
    Args:
        bot: Экземпляр бота
        user: Новый пользователь
    """
    if not config.NOTIFY_NEW_USERS:
        return
    
    name = user.first_name or 'Unknown'
    if user.last_name:
        name += f' {user.last_name}'
    
    username = user.username or 'нет'
    
    text = get_text(
        'admin.new_user',
        'ru',  # Уведомления админам на русском
        user_id=user.telegram_id,
        name=name,
        username=username,
        language=user.language or 'не выбран',
    )
    
    await notify_admins(bot, text)


async def notify_new_payment(
    bot: Bot,
    user: User,
    tariff_name: str,
    amount: float,
) -> None:
    """
    Уведомить админов о новой оплате.
    
    Args:
        bot: Экземпляр бота
        user: Пользователь
        tariff_name: Название тарифа
        amount: Сумма оплаты
    """
    if not config.NOTIFY_PAYMENTS:
        return
    
    name = user.first_name or 'Unknown'
    username = user.username or 'нет'
    
    text = get_text(
        'admin.new_payment',
        'ru',
        user_id=user.telegram_id,
        name=name,
        username=username,
        tariff=tariff_name,
        amount=f"{amount:.2f}",
    )
    
    await notify_admins(bot, text)
