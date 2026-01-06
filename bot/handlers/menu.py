"""
Обработка статического меню (fallback если БД пустая).
Обработчик menu:main перенесён в menu_navigation.py
"""

from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from bot.models import User, Subscription, Tariff
from bot.keyboards import language_keyboard, support_keyboard, back_to_menu_keyboard, tariffs_keyboard, subscriptions_keyboard
from bot.config import config
from bot.locales import get_text

router = Router()


# ВАЖНО: обработчик menu:main находится в menu_navigation.py!
# Здесь только вспомогательные обработчики для статических пунктов меню


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
    result = await session.execute(
        select(Subscription).where(
            Subscription.user_id == user.id,
            Subscription.is_active == True
        ).options(selectinload(Subscription.tariff))
    )
    subscriptions = result.scalars().all()
    
    if not subscriptions:
        await callback.message.edit_text(
            _('subscriptions.empty'),
            reply_markup=back_to_menu_keyboard(lang)
        )
    else:
        await callback.message.edit_text(
            _('subscriptions.title'),
            reply_markup=subscriptions_keyboard(subscriptions, lang)
        )
    await callback.answer()


@router.callback_query(F.data == "menu:tariffs")
async def menu_tariffs(
    callback: CallbackQuery,
    session: AsyncSession,
    lang: str,
    _: callable,
):
    """Показать тарифы."""
    result = await session.execute(
        select(Tariff).where(Tariff.is_active == True).order_by(Tariff.sort_order)
    )
    tariffs = result.scalars().all()
    
    await callback.message.edit_text(
        _('tariffs.title'),
        reply_markup=tariffs_keyboard(tariffs, lang)
    )
    await callback.answer()


@router.callback_query(F.data == "menu:promocode")
async def menu_promocode(
    callback: CallbackQuery,
    lang: str,
    _: callable,
):
    """Показать ввод промокода."""
    await callback.message.edit_text(
        _('promocode.enter'),
        reply_markup=back_to_menu_keyboard(lang)
    )
    await callback.answer()

