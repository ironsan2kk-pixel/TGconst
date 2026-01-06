"""
Обработчик главного меню
"""
from typing import Any, Dict
from aiogram import Router, F
from aiogram.types import Message

from ..database import get_user_by_telegram_id, get_user_subscriptions
from ..keyboards.reply import get_main_menu_keyboard
from ..keyboards.inline import get_channels_keyboard

router = Router(name="menu")


# Тексты кнопок главного меню
MENU_CHANNELS = "📢 Каналы"
MENU_MY_SUBS = "📋 Мои подписки"
MENU_SUPPORT = "💬 Поддержка"
MENU_PROMO = "🎁 Промокод"


@router.message(F.text == MENU_CHANNELS)
async def show_channels(message: Message):
    """Показать список доступных каналов"""
    keyboard = await get_channels_keyboard()
    
    if not keyboard:
        await message.answer(
            "😔 К сожалению, сейчас нет доступных каналов.\n"
            "Попробуйте позже!",
            reply_markup=get_main_menu_keyboard()
        )
        return
    
    await message.answer(
        "📢 <b>Доступные каналы</b>\n\n"
        "Выберите канал для просмотра тарифов:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )


# Обработчики для кнопок "📋 Мои подписки", "💬 Поддержка", "🎁 Промокод"
# перенесены в отдельные файлы:
# - handlers/subscription.py
# - handlers/support.py  
# - handlers/promocode.py
