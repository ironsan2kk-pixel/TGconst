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
        reply_markup=keyboard
    )


@router.message(F.text == MENU_MY_SUBS)
async def show_my_subscriptions(message: Message):
    """Показать подписки пользователя"""
    user = await get_user_by_telegram_id(message.from_user.id)
    
    if not user:
        await message.answer(
            "😔 Информация о вас не найдена.\n"
            "Нажмите /start чтобы начать.",
            reply_markup=get_main_menu_keyboard()
        )
        return
    
    subscriptions = await get_user_subscriptions(user["id"], active_only=True)
    
    if not subscriptions:
        await message.answer(
            "📋 <b>Мои подписки</b>\n\n"
            "У вас пока нет активных подписок.\n\n"
            "Нажмите «📢 Каналы» чтобы оформить подписку!",
            reply_markup=get_main_menu_keyboard()
        )
        return
    
    # Формируем список подписок
    text = "📋 <b>Мои подписки</b>\n\n"
    
    for sub in subscriptions:
        channel_name = sub.get("channel_title", "Канал")
        expires_at = sub.get("expires_at", "")
        
        # Форматируем дату
        if expires_at:
            from datetime import datetime
            try:
                exp_date = datetime.fromisoformat(expires_at)
                expires_str = exp_date.strftime("%d.%m.%Y %H:%M")
            except:
                expires_str = expires_at
        else:
            expires_str = "Бессрочно"
        
        text += f"• <b>{channel_name}</b>\n"
        text += f"  ⏰ До: {expires_str}\n\n"
    
    await message.answer(text, reply_markup=get_main_menu_keyboard())


@router.message(F.text == MENU_SUPPORT)
async def show_support(message: Message, bot_config: Dict[str, Any] = None):
    """Показать информацию о поддержке"""
    # Получаем URL поддержки из конфига
    bot_config = bot_config or {}
    support_url = bot_config.get("support_url")
    
    if support_url:
        text = (
            "💬 <b>Поддержка</b>\n\n"
            "Если у вас возникли вопросы или проблемы, "
            f"свяжитесь с нашей поддержкой:\n\n👉 {support_url}"
        )
    else:
        text = (
            "💬 <b>Поддержка</b>\n\n"
            "К сожалению, контакт поддержки не настроен.\n"
            "Попробуйте обратиться позже."
        )
    
    await message.answer(text, reply_markup=get_main_menu_keyboard())


@router.message(F.text == MENU_PROMO)
async def show_promo_info(message: Message):
    """Показать информацию о промокодах"""
    text = (
        "🎁 <b>Промокод</b>\n\n"
        "Если у вас есть промокод, вы сможете применить его "
        "при оплате тарифа для получения скидки.\n\n"
        "Выберите канал и тариф, затем введите промокод!"
    )
    
    await message.answer(text, reply_markup=get_main_menu_keyboard())
