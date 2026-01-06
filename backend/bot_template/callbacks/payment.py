"""
Callback обработчики для платежей
Обрабатывает deeplink после успешной оплаты в CryptoBot
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, CommandObject
from sqlalchemy import select, and_
from datetime import datetime
import logging

from ..database import get_session
from ..models import User, Subscription, Channel, Tariff

logger = logging.getLogger(__name__)

router = Router()


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
    
    async with get_session() as session:
        # Получаем пользователя
        stmt = select(User).where(User.telegram_id == message.from_user.id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            await message.answer("❌ Пользователь не найден")
            return
        
        # Проверяем есть ли активная подписка
        stmt = select(Subscription).where(
            and_(
                Subscription.user_id == user.id,
                Subscription.tariff_id == tariff_id,
                Subscription.is_active == True,
                Subscription.expires_at > datetime.utcnow()
            )
        ).order_by(Subscription.created_at.desc())
        
        result = await session.execute(stmt)
        subscription = result.scalar_one_or_none()
        
        if subscription:
            # Подписка уже активна
            stmt = select(Channel).where(Channel.id == subscription.channel_id)
            result = await session.execute(stmt)
            channel = result.scalar_one_or_none()
            
            stmt = select(Tariff).where(Tariff.id == tariff_id)
            result = await session.execute(stmt)
            tariff = result.scalar_one_or_none()
            
            expires_at_str = subscription.expires_at.strftime("%d.%m.%Y %H:%M")
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📋 Мои подписки", callback_data="my_subscriptions")],
                [InlineKeyboardButton(text="🏠 В меню", callback_data="main_menu")]
            ])
            
            await message.answer(
                f"✅ <b>Оплата прошла успешно!</b>\n\n"
                f"📺 Канал: <b>{channel.title if channel else 'Неизвестно'}</b>\n"
                f"📋 Тариф: <b>{tariff.name if tariff else 'Неизвестно'}</b>\n"
                f"📅 Действует до: <b>{expires_at_str}</b>\n\n"
                f"Вы будете добавлены в канал автоматически.",
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        else:
            # Подписка не найдена - возможно ещё обрабатывается webhook
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔄 Проверить статус", callback_data=f"check_sub_status:{tariff_id}")],
                [InlineKeyboardButton(text="🏠 В меню", callback_data="main_menu")]
            ])
            
            await message.answer(
                "⏳ <b>Обрабатываем вашу оплату...</b>\n\n"
                "Если оплата прошла успешно, подписка будет активирована в течение минуты.\n\n"
                "Нажмите кнопку ниже для проверки статуса.",
                reply_markup=keyboard,
                parse_mode="HTML"
            )


@router.callback_query(F.data.startswith("check_sub_status:"))
async def handle_check_subscription_status(callback: CallbackQuery):
    """Проверка статуса подписки"""
    await callback.answer()
    
    tariff_id = int(callback.data.split(":")[1])
    
    async with get_session() as session:
        # Получаем пользователя
        stmt = select(User).where(User.telegram_id == callback.from_user.id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            await callback.message.edit_text("❌ Пользователь не найден")
            return
        
        # Проверяем подписку
        stmt = select(Subscription).where(
            and_(
                Subscription.user_id == user.id,
                Subscription.tariff_id == tariff_id,
                Subscription.is_active == True,
                Subscription.expires_at > datetime.utcnow()
            )
        ).order_by(Subscription.created_at.desc())
        
        result = await session.execute(stmt)
        subscription = result.scalar_one_or_none()
        
        if subscription:
            # Подписка активирована
            stmt = select(Channel).where(Channel.id == subscription.channel_id)
            result = await session.execute(stmt)
            channel = result.scalar_one_or_none()
            
            stmt = select(Tariff).where(Tariff.id == tariff_id)
            result = await session.execute(stmt)
            tariff = result.scalar_one_or_none()
            
            expires_at_str = subscription.expires_at.strftime("%d.%m.%Y %H:%M")
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📋 Мои подписки", callback_data="my_subscriptions")],
                [InlineKeyboardButton(text="🏠 В меню", callback_data="main_menu")]
            ])
            
            await callback.message.edit_text(
                f"✅ <b>Подписка активирована!</b>\n\n"
                f"📺 Канал: <b>{channel.title if channel else 'Неизвестно'}</b>\n"
                f"📋 Тариф: <b>{tariff.name if tariff else 'Неизвестно'}</b>\n"
                f"📅 Действует до: <b>{expires_at_str}</b>\n\n"
                f"Вы будете добавлены в канал автоматически.",
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        else:
            # Ещё не активирована
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔄 Проверить ещё раз", callback_data=f"check_sub_status:{tariff_id}")],
                [InlineKeyboardButton(text="💬 Поддержка", callback_data="support")],
                [InlineKeyboardButton(text="🏠 В меню", callback_data="main_menu")]
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
