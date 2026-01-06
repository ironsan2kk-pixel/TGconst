"""
Хендлеры для просмотра подписок пользователя.
"""

from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import User
from bot.locales import get_text
from bot.keyboards.inline import (
    subscriptions_keyboard,
    subscription_detail_keyboard,
    back_to_menu_keyboard,
)
from bot.services.subscription import get_user_subscriptions

router = Router()


@router.callback_query(F.data == "menu:subscriptions")
@router.callback_query(F.data == "my_subscriptions")
async def show_subscriptions(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    lang: str,
    _: Callable,
):
    """Показать список подписок пользователя."""
    subscriptions = await get_user_subscriptions(
        session=session,
        user_id=user.id,
        active_only=True,
    )
    
    if not subscriptions:
        await callback.message.edit_text(
            _('subscriptions.empty'),
            reply_markup=back_to_menu_keyboard(lang)
        )
        await callback.answer()
        return
    
    # Формируем список подписок
    text = f"💳 <b>{_('subscriptions.title')}</b>\n\n"
    
    for sub in subscriptions:
        tariff = sub.tariff
        tariff_name = tariff.name_ru if lang == 'ru' else tariff.name_en
        
        # Количество каналов
        channels_count = len(tariff.tariff_channels) if tariff.tariff_channels else 0
        
        if sub.expires_at:
            expires = sub.expires_at.strftime('%d.%m.%Y')
            item_text = _('subscriptions.item').format(
                tariff=tariff_name,
                expires=expires,
                channels_count=channels_count,
            )
        else:
            item_text = _('subscriptions.item_forever').format(
                tariff=tariff_name,
                channels_count=channels_count,
            )
        
        # Добавляем пометку о пробном периоде
        if sub.is_trial:
            item_text += _('subscriptions.item_trial')
        
        text += item_text + "\n\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=subscriptions_keyboard(subscriptions, lang)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("subscription:"))
async def show_subscription_detail(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    lang: str,
    _: Callable,
):
    """Показать детали подписки."""
    subscription_id = int(callback.data.split(':')[1])
    
    # Получаем все подписки и ищем нужную
    subscriptions = await get_user_subscriptions(
        session=session,
        user_id=user.id,
        active_only=True,
    )
    
    subscription = None
    for sub in subscriptions:
        if sub.id == subscription_id:
            subscription = sub
            break
    
    if not subscription:
        await callback.answer(_('error'), show_alert=True)
        return
    
    tariff = subscription.tariff
    tariff_name = tariff.name_ru if lang == 'ru' else tariff.name_en
    
    # Количество каналов
    channels_count = len(tariff.tariff_channels) if tariff.tariff_channels else 0
    
    # Статус
    if subscription.is_trial:
        status = _('subscriptions.status_trial')
    elif subscription.expires_at:
        from datetime import datetime
from typing import Callable
        now = datetime.utcnow()
        days_left = (subscription.expires_at - now).days
        if days_left <= 3:
            status = _('subscriptions.status_expiring')
        else:
            status = _('subscriptions.status_active')
    else:
        status = _('subscriptions.status_active')
    
    # Формируем текст
    starts = subscription.starts_at.strftime('%d.%m.%Y') if subscription.starts_at else "-"
    
    if subscription.expires_at:
        expires = subscription.expires_at.strftime('%d.%m.%Y %H:%M')
    else:
        if lang == 'ru':
            expires = "Навсегда"
        else:
            expires = "Forever"
    
    text = _('subscriptions.detail').format(
        tariff=tariff_name,
        starts=starts,
        expires=expires,
        channels_count=channels_count,
        status=status,
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=subscription_detail_keyboard(subscription, lang)
    )
    await callback.answer()


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    lang: str,
    _: Callable,
):
    """Вернуться в главное меню."""
    from bot.keyboards.inline import main_menu_keyboard
    from bot.services.subscription import get_user_subscriptions
    
    # Проверяем есть ли подписка
    subscriptions = await get_user_subscriptions(session, user.id, active_only=True)
    has_subscription = len(subscriptions) > 0
    
    await callback.message.edit_text(
        _('menu.title'),
        reply_markup=main_menu_keyboard(lang, has_subscription)
    )
    await callback.answer()
