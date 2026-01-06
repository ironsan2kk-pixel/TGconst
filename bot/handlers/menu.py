"""
Обработка главного меню.
"""

from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from bot.models import User, Subscription
from bot.keyboards import main_menu_keyboard, language_keyboard, support_keyboard
from bot.config import config
from bot.locales import get_text

router = Router()


@router.callback_query(F.data == "menu:main")
async def menu_main(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    lang: str,
    _: callable,
):
    """Возврат в главное меню."""
    # Проверяем наличие активной подписки
    result = await session.execute(
        select(Subscription).where(
            Subscription.user_id == user.id,
            Subscription.is_active == True
        )
    )
    has_subscription = result.scalar_one_or_none() is not None
    
    await callback.message.edit_text(
        _('menu.title'),
        reply_markup=main_menu_keyboard(lang, has_subscription)
    )
    await callback.answer()


@router.callback_query(F.data == "menu:language")
async def menu_language(
    callback: CallbackQuery,
    _: callable,
):
    """Показать выбор языка."""
    await callback.message.edit_text(
        _('choose_language'),
        reply_markup=language_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "menu:support")
async def menu_support(
    callback: CallbackQuery,
    lang: str,
    _: callable,
):
    """Показать поддержку."""
    support_url = config.SUPPORT_URL
    
    await callback.message.edit_text(
        _('support.text'),
        reply_markup=support_keyboard(support_url, lang)
    )
    await callback.answer()


@router.callback_query(F.data == "menu:subscriptions")
async def menu_subscriptions(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    lang: str,
    _: callable,
):
    """Показать подписки пользователя."""
    # Будет реализовано в Чат 5
    from bot.keyboards import back_to_menu_keyboard
    
    result = await session.execute(
        select(Subscription).where(
            Subscription.user_id == user.id,
            Subscription.is_active == True
        )
    )
    subscriptions = result.scalars().all()
    
    if not subscriptions:
        await callback.message.edit_text(
            _('subscriptions.empty'),
            reply_markup=back_to_menu_keyboard(lang)
        )
    else:
        # Формируем список подписок (базовая реализация)
        text = _('subscriptions.title') + '\n\n'
        
        for sub in subscriptions:
            if sub.expires_at:
                expires = sub.expires_at.strftime('%d.%m.%Y')
                text += _('subscriptions.item', 
                         tariff=f"Тариф #{sub.tariff_id}",
                         expires=expires,
                         channels_count=0) + '\n\n'
            else:
                text += _('subscriptions.item_forever',
                         tariff=f"Тариф #{sub.tariff_id}",
                         channels_count=0) + '\n\n'
        
        await callback.message.edit_text(
            text,
            reply_markup=back_to_menu_keyboard(lang)
        )
    
    await callback.answer()


@router.callback_query(F.data == "menu:promocode")
async def menu_promocode(
    callback: CallbackQuery,
    lang: str,
    _: callable,
):
    """Показать ввод промокода."""
    # Будет реализовано в Чат 5
    from bot.keyboards import back_to_menu_keyboard
    
    await callback.message.edit_text(
        _('promocode.enter'),
        reply_markup=back_to_menu_keyboard(lang)
    )
    await callback.answer()
