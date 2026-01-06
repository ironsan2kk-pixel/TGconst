"""
Обработка команды /start и deep links.
"""

from aiogram import Router, F
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from bot.models import User, Subscription, Tariff, MenuItem
from bot.keyboards import language_keyboard, main_menu_keyboard, dynamic_menu_keyboard
from bot.locales import get_text

router = Router()


async def get_menu_items_from_db(
    session: AsyncSession,
    parent_id: int | None = None,
    has_subscription: bool = False,
    language: str = 'ru'
) -> list[MenuItem]:
    """Получить пункты меню из БД."""
    query = select(MenuItem).where(
        MenuItem.parent_id == parent_id,
        MenuItem.is_active == True
    ).order_by(MenuItem.sort_order)
    
    result = await session.execute(query)
    items = result.scalars().all()
    
    filtered = []
    for item in items:
        if item.visibility_language and item.visibility_language != 'all':
            if item.visibility_language != language:
                continue
        if item.visibility == 'subscribed' and not has_subscription:
            continue
        if item.visibility == 'not_subscribed' and has_subscription:
            continue
        filtered.append(item)
    
    return filtered


async def show_main_menu(
    message: Message,
    session: AsyncSession,
    user: User,
    lang: str,
):
    """Показать главное меню."""
    _ = lambda key, **kw: get_text(key, lang, **kw)
    
    # Проверяем подписку
    result = await session.execute(
        select(Subscription).where(
            Subscription.user_id == user.id,
            Subscription.is_active == True
        )
    )
    has_subscription = result.scalar_one_or_none() is not None
    
    # Пробуем загрузить из БД
    items = await get_menu_items_from_db(session, None, has_subscription, lang)
    
    if items:
        keyboard = dynamic_menu_keyboard(items, lang)
    else:
        keyboard = main_menu_keyboard(lang, has_subscription)
    
    await message.answer(_('menu.title'), reply_markup=keyboard)


@router.message(CommandStart(deep_link=True))
async def cmd_start_deep_link(
    message: Message,
    command: CommandObject,
    session: AsyncSession,
    user: User,
    lang: str,
    _: callable,
    is_new_user: bool,
):
    """Обработка /start с deep link."""
    deep_link = command.args
    
    if not deep_link:
        return await cmd_start(message, session, user, lang, _, is_new_user)
    
    if deep_link.startswith('tariff_'):
        try:
            tariff_id = int(deep_link.replace('tariff_', ''))
            from bot.handlers.tariffs import show_tariff_detail
            await show_tariff_detail(message, session, user, lang, _, tariff_id)
            return
        except (ValueError, TypeError):
            pass
    
    await cmd_start(message, session, user, lang, _, is_new_user)


@router.message(CommandStart())
async def cmd_start(
    message: Message,
    session: AsyncSession,
    user: User,
    lang: str,
    _: callable,
    is_new_user: bool,
):
    """Обработка команды /start."""
    
    if is_new_user:
        await message.answer(
            get_text('welcome'),
            reply_markup=language_keyboard()
        )
    else:
        name = user.first_name or 'друг'
        await message.answer(_('welcome_back', name=name))
        await show_main_menu(message, session, user, lang)


@router.message(F.text == '/menu')
async def cmd_menu(
    message: Message,
    session: AsyncSession,
    user: User,
    lang: str,
    _: callable,
):
    """Команда /menu."""
    await show_main_menu(message, session, user, lang)
