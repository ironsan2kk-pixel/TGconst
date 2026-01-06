"""
Callback обработчики для платежей
Обрабатывает deeplink после успешной оплаты в CryptoBot
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, CommandObject
from datetime import datetime
import logging

from ..database import (
    get_user_by_telegram_id,
    get_user_subscriptions,
    get_channel_by_id,
    get_tariff_by_id
)
from ..keyboards.inline import get_back_to_channels_keyboard

logger = logging.getLogger(__name__)

router = Router(name="payment_callbacks")


@router.message(CommandStart(deep_link=True, magic=F.args.startswith("paid_")))
async def handle_paid_deeplink(message: Message, command: CommandObject):
    """
    Обработка deeplink после оплаты в CryptoBot
    Формат: /start paid_{tariff_id}
    """
    if not command.args:
        return
    
    try:
        tariff_id = int(command.args.replace("paid_", ""))
    except ValueError:
        return
    
    # Получаем пользователя
    user = await get_user_by_telegram_id(message.from_user.id)
    
    if not user:
        await message.answer("❌ Пользователь не найден. Нажмите /start")
        return
    
    # Получаем тариф
    tariff = await get_tariff_by_id(tariff_id)
    
    if not tariff:
        await message.answer("❌ Тариф не найден")
        return
    
    # Получаем канал
    channel = await get_channel_by_id(tariff["channel_id"])
    
    # Проверяем подписки пользователя
    subscriptions = await get_user_subscriptions(user["id"], active_only=True)
    
    # Ищем подписку на этот канал
    has_subscription = False
    expires_at = None
    
    for sub in subscriptions:
        if sub["channel_id"] == tariff["channel_id"]:
            has_subscription = True
            expires_at = sub["expires_at"]
            break
    
    keyboard = get_back_to_channels_keyboard()
    
    if has_subscription:
        # Форматируем дату
        if isinstance(expires_at, str):
            expires_at_dt = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
        else:
            expires_at_dt = expires_at
        
        expires_at_str = expires_at_dt.strftime("%d.%m.%Y %H:%M") if expires_at_dt else "Неизвестно"
        
        await message.answer(
            f"✅ <b>Оплата прошла успешно!</b>\n\n"
            f"📺 Канал: <b>{channel['title'] if channel else 'Неизвестно'}</b>\n"
            f"📋 Тариф: <b>{tariff['name']}</b>\n"
            f"📅 Действует до: <b>{expires_at_str}</b>\n\n"
            f"Вы будете добавлены в канал автоматически.",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    else:
        # Подписка ещё не создана - webhook возможно ещё не обработан
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Проверить статус", callback_data=f"check_sub:{tariff_id}")],
            [InlineKeyboardButton(text="◀️ К каналам", callback_data="back_to_channels")]
        ])
        
        await message.answer(
            "⏳ <b>Обрабатываем вашу оплату...</b>\n\n"
            "Если оплата прошла успешно, подписка будет активирована в течение минуты.\n\n"
            "Нажмите кнопку ниже для проверки статуса.",
            reply_markup=keyboard,
            parse_mode="HTML"
        )


@router.callback_query(F.data.startswith("check_sub:"))
async def handle_check_subscription_status(callback: CallbackQuery):
    """Проверка статуса подписки"""
    await callback.answer()
    
    tariff_id = int(callback.data.split(":")[1])
    
    # Получаем пользователя
    user = await get_user_by_telegram_id(callback.from_user.id)
    
    if not user:
        await callback.message.edit_text("❌ Пользователь не найден")
        return
    
    # Получаем тариф
    tariff = await get_tariff_by_id(tariff_id)
    
    if not tariff:
        await callback.message.edit_text("❌ Тариф не найден")
        return
    
    # Получаем канал
    channel = await get_channel_by_id(tariff["channel_id"])
    
    # Проверяем подписки
    subscriptions = await get_user_subscriptions(user["id"], active_only=True)
    
    has_subscription = False
    expires_at = None
    
    for sub in subscriptions:
        if sub["channel_id"] == tariff["channel_id"]:
            has_subscription = True
            expires_at = sub["expires_at"]
            break
    
    if has_subscription:
        # Форматируем дату
        if isinstance(expires_at, str):
            expires_at_dt = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
        else:
            expires_at_dt = expires_at
        
        expires_at_str = expires_at_dt.strftime("%d.%m.%Y %H:%M") if expires_at_dt else "Неизвестно"
        
        keyboard = get_back_to_channels_keyboard()
        
        await callback.message.edit_text(
            f"✅ <b>Подписка активирована!</b>\n\n"
            f"📺 Канал: <b>{channel['title'] if channel else 'Неизвестно'}</b>\n"
            f"📋 Тариф: <b>{tariff['name']}</b>\n"
            f"📅 Действует до: <b>{expires_at_str}</b>\n\n"
            f"Вы будете добавлены в канал автоматически.",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    else:
        # Ещё не активирована
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Проверить ещё раз", callback_data=f"check_sub:{tariff_id}")],
            [InlineKeyboardButton(text="◀️ К каналам", callback_data="back_to_channels")]
        ])
        
        await callback.message.edit_text(
            "⏳ <b>Подписка ещё не активирована</b>\n\n"
            "Если вы уже оплатили, подождите немного и проверьте снова.\n"
            "Обычно активация занимает до 1 минуты.\n\n"
            "Если подписка не активируется в течение 5 минут, "
            "обратитесь в поддержку.",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
