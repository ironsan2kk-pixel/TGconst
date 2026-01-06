"""
Обработчик подписок пользователя
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime, timedelta
from typing import List, Optional
import logging

from ..database import (
    get_user_by_telegram_id,
    get_user_subscriptions,
    get_channel_by_id,
    get_tariffs_by_channel,
    get_active_subscription
)
from ..keyboards.reply import get_main_menu_keyboard

logger = logging.getLogger(__name__)

router = Router(name="subscription")


def format_time_remaining(expires_at: str) -> str:
    """Форматирование оставшегося времени"""
    try:
        exp_date = datetime.fromisoformat(expires_at)
        now = datetime.utcnow()
        
        if exp_date <= now:
            return "Истекла"
        
        diff = exp_date - now
        days = diff.days
        hours = diff.seconds // 3600
        
        if days > 30:
            months = days // 30
            return f"~{months} мес."
        elif days > 0:
            return f"{days} дн. {hours} ч."
        elif hours > 0:
            minutes = (diff.seconds % 3600) // 60
            return f"{hours} ч. {minutes} мин."
        else:
            minutes = diff.seconds // 60
            return f"{minutes} мин."
    except:
        return "Неизвестно"


def get_subscription_status_emoji(expires_at: str) -> str:
    """Получить эмодзи статуса подписки"""
    try:
        exp_date = datetime.fromisoformat(expires_at)
        now = datetime.utcnow()
        diff = exp_date - now
        
        if diff.days < 0:
            return "❌"  # Истекла
        elif diff.days <= 3:
            return "⚠️"  # Скоро истечёт
        elif diff.days <= 7:
            return "🟡"  # Менее недели
        else:
            return "✅"  # Активна
    except:
        return "❓"


@router.message(F.text == "📋 Мои подписки")
async def show_subscriptions(message: Message):
    """Показать подписки пользователя"""
    user = await get_user_by_telegram_id(message.from_user.id)
    
    if not user:
        await message.answer(
            "😔 Информация о вас не найдена.\n"
            "Нажмите /start чтобы начать.",
            reply_markup=get_main_menu_keyboard()
        )
        return
    
    # Получаем все подписки (включая неактивные)
    all_subscriptions = await get_user_subscriptions(user["id"], active_only=False)
    active_subscriptions = [s for s in all_subscriptions if s.get("is_active")]
    
    builder = InlineKeyboardBuilder()
    
    if not all_subscriptions:
        await message.answer(
            "📋 <b>Мои подписки</b>\n\n"
            "У вас пока нет подписок.\n\n"
            "Нажмите «📢 Каналы» чтобы оформить первую подписку!",
            reply_markup=get_main_menu_keyboard(),
            parse_mode="HTML"
        )
        return
    
    if not active_subscriptions:
        # Есть история, но нет активных
        text = (
            "📋 <b>Мои подписки</b>\n\n"
            "⚠️ У вас нет активных подписок.\n\n"
            "📊 <b>История:</b>\n"
        )
        
        for sub in all_subscriptions[:5]:  # Показываем последние 5
            channel_name = sub.get("channel_title", "Канал")
            expires_at = sub.get("expires_at", "")
            
            if expires_at:
                try:
                    exp_date = datetime.fromisoformat(expires_at)
                    exp_str = exp_date.strftime("%d.%m.%Y")
                except:
                    exp_str = "—"
            else:
                exp_str = "—"
            
            text += f"• {channel_name} — истекла {exp_str}\n"
        
        text += "\nОформите новую подписку!"
        
        builder.button(text="📢 Каналы", callback_data="back_to_channels")
        
        await message.answer(
            text,
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )
        return
    
    # Есть активные подписки
    text = "📋 <b>Мои подписки</b>\n\n"
    
    for sub in active_subscriptions:
        channel_name = sub.get("channel_title", "Канал")
        channel_username = sub.get("channel_username", "")
        expires_at = sub.get("expires_at", "")
        
        status_emoji = get_subscription_status_emoji(expires_at)
        time_remaining = format_time_remaining(expires_at)
        
        # Форматируем дату окончания
        if expires_at:
            try:
                exp_date = datetime.fromisoformat(expires_at)
                exp_str = exp_date.strftime("%d.%m.%Y %H:%M")
            except:
                exp_str = expires_at
        else:
            exp_str = "Бессрочно"
        
        text += f"{status_emoji} <b>{channel_name}</b>\n"
        if channel_username:
            text += f"   📎 @{channel_username}\n"
        text += f"   ⏰ До: {exp_str}\n"
        text += f"   ⏳ Осталось: {time_remaining}\n\n"
        
        # Кнопка продления для каждой подписки
        builder.button(
            text=f"🔄 Продлить «{channel_name[:15]}...»" if len(channel_name) > 15 else f"🔄 Продлить «{channel_name}»",
            callback_data=f"extend_sub:{sub['channel_id']}"
        )
    
    builder.button(text="📢 Все каналы", callback_data="back_to_channels")
    builder.adjust(1)
    
    # Добавляем легенду
    text += (
        "━━━━━━━━━━━━━━━\n"
        "✅ — активна | ⚠️ — скоро истечёт\n"
        "🟡 — менее недели | ❌ — истекла"
    )
    
    await message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")


@router.callback_query(F.data.startswith("extend_sub:"))
async def extend_subscription(callback: CallbackQuery):
    """Продление подписки - переход к тарифам канала"""
    await callback.answer()
    
    channel_id = int(callback.data.split(":")[1])
    
    # Получаем канал
    channel = await get_channel_by_id(channel_id)
    if not channel:
        await callback.message.edit_text("❌ Канал не найден")
        return
    
    # Получаем тарифы
    tariffs = await get_tariffs_by_channel(channel_id)
    
    if not tariffs:
        builder = InlineKeyboardBuilder()
        builder.button(text="◀️ Назад", callback_data="back_to_subs")
        
        await callback.message.edit_text(
            f"❌ Для канала «{channel['title']}» нет доступных тарифов.",
            reply_markup=builder.as_markup()
        )
        return
    
    # Проверяем текущую подписку
    user = await get_user_by_telegram_id(callback.from_user.id)
    current_sub = await get_active_subscription(user["id"], channel_id) if user else None
    
    builder = InlineKeyboardBuilder()
    
    text = f"🔄 <b>Продление подписки</b>\n\n"
    text += f"📺 Канал: <b>{channel['title']}</b>\n"
    
    if current_sub and current_sub.get("expires_at"):
        time_remaining = format_time_remaining(current_sub["expires_at"])
        text += f"⏳ Текущая подписка: {time_remaining}\n"
    
    text += "\n<b>Выберите тариф:</b>\n\n"
    
    for tariff in tariffs:
        days = tariff["duration_days"]
        if days == 30:
            duration = "1 месяц"
        elif days == 90:
            duration = "3 месяца"
        elif days == 180:
            duration = "6 месяцев"
        elif days == 365:
            duration = "1 год"
        else:
            duration = f"{days} дней"
        
        text += f"• <b>{tariff['name']}</b> — ${tariff['price']:.2f} ({duration})\n"
        
        builder.button(
            text=f"💳 {tariff['name']} — ${tariff['price']:.2f}",
            callback_data=f"tariff:{tariff['id']}"
        )
    
    builder.button(text="◀️ Назад к подпискам", callback_data="back_to_subs")
    builder.adjust(1)
    
    text += "\n💡 <i>При продлении дни добавляются к текущей подписке</i>"
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")


@router.callback_query(F.data == "back_to_subs")
async def back_to_subscriptions(callback: CallbackQuery):
    """Возврат к списку подписок"""
    await callback.answer()
    
    user = await get_user_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.message.edit_text("❌ Пользователь не найден")
        return
    
    subscriptions = await get_user_subscriptions(user["id"], active_only=True)
    
    builder = InlineKeyboardBuilder()
    
    if not subscriptions:
        text = (
            "📋 <b>Мои подписки</b>\n\n"
            "У вас нет активных подписок."
        )
        builder.button(text="📢 Каналы", callback_data="back_to_channels")
    else:
        text = "📋 <b>Мои подписки</b>\n\n"
        
        for sub in subscriptions:
            channel_name = sub.get("channel_title", "Канал")
            expires_at = sub.get("expires_at", "")
            
            status_emoji = get_subscription_status_emoji(expires_at)
            time_remaining = format_time_remaining(expires_at)
            
            if expires_at:
                try:
                    exp_date = datetime.fromisoformat(expires_at)
                    exp_str = exp_date.strftime("%d.%m.%Y %H:%M")
                except:
                    exp_str = expires_at
            else:
                exp_str = "Бессрочно"
            
            text += f"{status_emoji} <b>{channel_name}</b>\n"
            text += f"   ⏰ До: {exp_str}\n"
            text += f"   ⏳ Осталось: {time_remaining}\n\n"
            
            builder.button(
                text=f"🔄 Продлить «{channel_name[:15]}»",
                callback_data=f"extend_sub:{sub['channel_id']}"
            )
        
        builder.button(text="📢 Все каналы", callback_data="back_to_channels")
    
    builder.adjust(1)
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")


@router.callback_query(F.data == "sub_details")
async def subscription_details(callback: CallbackQuery):
    """Детальная информация о подписках"""
    await callback.answer()
    
    user = await get_user_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.message.edit_text("❌ Пользователь не найден")
        return
    
    all_subs = await get_user_subscriptions(user["id"], active_only=False)
    
    if not all_subs:
        await callback.answer("У вас нет истории подписок", show_alert=True)
        return
    
    builder = InlineKeyboardBuilder()
    
    text = "📊 <b>Статистика подписок</b>\n\n"
    
    active_count = sum(1 for s in all_subs if s.get("is_active"))
    expired_count = len(all_subs) - active_count
    
    text += f"✅ Активных: {active_count}\n"
    text += f"❌ Истёкших: {expired_count}\n"
    text += f"📋 Всего: {len(all_subs)}\n\n"
    
    text += "<b>Последние 10:</b>\n"
    
    for sub in all_subs[:10]:
        channel_name = sub.get("channel_title", "Канал")
        is_active = sub.get("is_active")
        expires_at = sub.get("expires_at", "")
        
        status = "✅" if is_active else "❌"
        
        if expires_at:
            try:
                exp_date = datetime.fromisoformat(expires_at)
                exp_str = exp_date.strftime("%d.%m.%y")
            except:
                exp_str = "—"
        else:
            exp_str = "∞"
        
        text += f"{status} {channel_name} — {exp_str}\n"
    
    builder.button(text="◀️ Назад", callback_data="back_to_subs")
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
