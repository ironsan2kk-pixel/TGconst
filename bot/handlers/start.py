"""
Обработка команды /start и deep links.
"""

from aiogram import Router, F
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from bot.models import User, Subscription, Tariff
from bot.keyboards import language_keyboard, main_menu_keyboard
from bot.locales import get_text

router = Router()


async def show_main_menu(
    message: Message,
    session: AsyncSession,
    user: User,
    lang: str,
):
    """Показать главное меню (динамическое из БД или статическое)."""
    from bot.handlers.menu_navigation import show_dynamic_menu, get_menu_items
    
    # Проверяем есть ли пункты меню в БД
    has_subscription = False
    result = await session.execute(
        select(Subscription).where(
            Subscription.user_id == user.id,
            Subscription.is_active == True
        )
    )
    has_subscription = result.scalar_one_or_none() is not None
    
    items = await get_menu_items(session, None, has_subscription, lang)
    
    if items:
        # Есть пункты в БД - используем динамическое меню
        await show_dynamic_menu(message, session, user, lang, parent_id=None, edit=False)
    else:
        # БД пустая - используем статическое меню
        _ = lambda key, **kw: get_text(key, lang, **kw)
        await message.answer(
            _('menu.title'),
            reply_markup=main_menu_keyboard(lang, has_subscription)
        )


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
    """
    Обработка /start с deep link.
    Формат: /start tariff_5 → открыть тариф #5
    """
    deep_link = command.args
    
    if not deep_link:
        return await cmd_start(message, session, user, lang, _, is_new_user)
    
    # Парсим deep link
    if deep_link.startswith('tariff_'):
        try:
            tariff_id = int(deep_link.replace('tariff_', ''))
            # Импортируем здесь чтобы избежать циклического импорта
            from bot.handlers.tariffs import show_tariff_detail
            await show_tariff_detail(message, session, user, lang, _, tariff_id)
            return
        except (ValueError, TypeError):
            pass
    
    # Если deep link не распознан, показываем обычный старт
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
        # Новый пользователь — показываем выбор языка
        await message.answer(
            get_text('welcome'),  # Текст на обоих языках
            reply_markup=language_keyboard()
        )
    else:
        # Существующий пользователь — показываем приветствие и меню
        name = user.first_name or 'друг'
        
        # Сначала приветствие
        await message.answer(_('welcome_back', name=name))
        
        # Затем меню
        await show_main_menu(message, session, user, lang)


@router.message(F.text == '/menu')
async def cmd_menu(
    message: Message,
    session: AsyncSession,
    user: User,
    lang: str,
    _: callable,
):
    """Команда /menu — показать главное меню."""
    await show_main_menu(message, session, user, lang)
