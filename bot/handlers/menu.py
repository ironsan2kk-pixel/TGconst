"""
Обработка главного меню.
"""

from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from bot.models import User, Subscription, MenuItem
from bot.keyboards import main_menu_keyboard, language_keyboard, support_keyboard, dynamic_menu_keyboard
from bot.config import config
from bot.locales import get_text

router = Router()


async def get_menu_items_from_db(
    session: AsyncSession,
    parent_id: int | None = None,
    has_subscription: bool = False,
    language: str = 'ru'
) -> list[MenuItem]:
    """Получить пункты меню из БД с учётом условий видимости."""
    query = select(MenuItem).where(
        MenuItem.parent_id == parent_id,
        MenuItem.is_active == True
    ).order_by(MenuItem.sort_order)
    
    result = await session.execute(query)
    items = result.scalars().all()
    
    # Фильтруем по условиям
    filtered = []
    for item in items:
        # Проверка языка
        if item.visibility_language and item.visibility_language != 'all':
            if item.visibility_language != language:
                continue
        
        # Проверка подписки
        if item.visibility == 'subscribed' and not has_subscription:
            continue
        if item.visibility == 'not_subscribed' and has_subscription:
            continue
        
        filtered.append(item)
    
    return filtered


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
    
    # Пробуем загрузить меню из БД
    items = await get_menu_items_from_db(session, None, has_subscription, lang)
    
    if items:
        # Используем динамическое меню из БД
        keyboard = dynamic_menu_keyboard(items, lang)
    else:
        # Fallback к статическому меню
        keyboard = main_menu_keyboard(lang, has_subscription)
    
    await callback.message.edit_text(
        _('menu.title'),
        reply_markup=keyboard
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
        # Формируем список подписок
        text = _('subscriptions.title') + '\n\n'
        # Базовая реализация - будет расширена в Чат 5
        for sub in subscriptions:
            text += f"• ID: {sub.id}\n"
        
        await callback.message.edit_text(
            text,
            reply_markup=back_to_menu_keyboard(lang)
        )
    await callback.answer()
