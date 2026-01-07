"""
Обработка смены языка.
"""

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from bot.models import User, Subscription
from bot.keyboards import language_keyboard, main_menu_keyboard
from bot.locales import get_text, get_available_languages

router = Router()


@router.message(Command('language'))
async def cmd_language(message: Message, _: callable):
    """Команда /language."""
    await message.answer(
        _('choose_language'),
        reply_markup=language_keyboard()
    )


@router.callback_query(F.data.startswith("lang:"))
async def change_language(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
):
    """Обработка выбора языка."""
    new_lang = callback.data.split(':')[1]
    
    if new_lang not in get_available_languages():
        await callback.answer("Unknown language", show_alert=True)
        return
    
    # Обновляем язык пользователя
    user.language = new_lang
    await session.flush()
    
    # Проверяем наличие активной подписки
    result = await session.execute(
        select(Subscription).where(
            Subscription.user_id == user.id,
            Subscription.is_active == True
        )
    )
    has_subscription = result.scalar_one_or_none() is not None
    
    # Отправляем подтверждение на новом языке
    await callback.message.edit_text(
        get_text('language_changed', new_lang),
        reply_markup=main_menu_keyboard(new_lang, has_subscription)
    )
    await callback.answer()
