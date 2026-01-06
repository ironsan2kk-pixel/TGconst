"""
Динамическая навигация по меню из БД.
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from bot.models import User, Subscription, MenuItem
from bot.locales import get_text

router = Router()


async def get_menu_items(
    session: AsyncSession,
    parent_id: int | None = None,
    user_has_subscription: bool = False,
    language: str = 'ru'
) -> list[MenuItem]:
    """Получить пункты меню с учётом условий видимости."""
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
        if item.visibility == 'subscribed' and not user_has_subscription:
            continue
        if item.visibility == 'not_subscribed' and user_has_subscription:
            continue
        
        filtered.append(item)
    
    return filtered


def build_menu_keyboard(
    items: list[MenuItem],
    lang: str,
    parent_id: int | None = None
):
    """Построить клавиатуру меню."""
    builder = InlineKeyboardBuilder()
    
    for item in items:
        text = item.text_ru if lang == 'ru' else (item.text_en or item.text_ru)
        if item.icon:
            text = f"{item.icon} {text}"
        
        if item.type == 'link' and item.value:
            # Внешняя ссылка
            builder.button(text=text, url=item.value)
        else:
            # Callback для всех остальных типов
            builder.button(text=text, callback_data=f"menu_item:{item.id}")
    
    # Кнопка "Назад" если мы в подменю
    if parent_id is not None:
        back_text = get_text('menu.back', lang)
        # Находим родителя чтобы вернуться на уровень выше
        builder.button(text=f"◀️ {back_text}", callback_data=f"menu_back:{parent_id}")
    
    builder.adjust(1)  # По одной кнопке в ряд
    return builder.as_markup()


async def check_user_subscription(session: AsyncSession, user_id: int) -> bool:
    """Проверить есть ли у пользователя активная подписка."""
    result = await session.execute(
        select(Subscription).where(
            Subscription.user_id == user_id,
            Subscription.is_active == True
        )
    )
    return result.scalar_one_or_none() is not None


async def show_dynamic_menu(
    message_or_callback,
    session: AsyncSession,
    user: User,
    lang: str,
    parent_id: int | None = None,
    edit: bool = True
):
    """Показать динамическое меню из БД."""
    _ = lambda key: get_text(key, lang)
    
    has_subscription = await check_user_subscription(session, user.id)
    items = await get_menu_items(session, parent_id, has_subscription, lang)
    
    # Если меню пустое - показываем заглушку
    if not items:
        # Fallback к статическому меню если таблица пустая
        from bot.keyboards import main_menu_keyboard
        keyboard = main_menu_keyboard(lang, has_subscription)
        text = _('menu.title')
    else:
        keyboard = build_menu_keyboard(items, lang, parent_id)
        
        # Заголовок
        if parent_id:
            # Получаем название раздела
            result = await session.execute(
                select(MenuItem).where(MenuItem.id == parent_id)
            )
            parent_item = result.scalar_one_or_none()
            if parent_item:
                title = parent_item.text_ru if lang == 'ru' else (parent_item.text_en or parent_item.text_ru)
                text = f"📁 {title}"
            else:
                text = _('menu.title')
        else:
            text = _('menu.title')
    
    if isinstance(message_or_callback, CallbackQuery):
        if edit:
            await message_or_callback.message.edit_text(text, reply_markup=keyboard)
        else:
            await message_or_callback.message.answer(text, reply_markup=keyboard)
        await message_or_callback.answer()
    else:
        await message_or_callback.answer(text, reply_markup=keyboard)


@router.callback_query(F.data.startswith("menu_item:"))
async def handle_menu_item(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    lang: str,
):
    """Обработка нажатия на пункт меню."""
    item_id = int(callback.data.split(":")[1])
    
    result = await session.execute(
        select(MenuItem).where(MenuItem.id == item_id)
    )
    item = result.scalar_one_or_none()
    
    if not item:
        await callback.answer("Пункт меню не найден", show_alert=True)
        return
    
    _ = lambda key: get_text(key, lang)
    
    if item.type == 'section':
        # Открыть подменю
        await show_dynamic_menu(callback, session, user, lang, parent_id=item.id)
    
    elif item.type == 'text':
        # Отправить текст
        text = item.value or "..."
        from bot.keyboards import back_to_menu_keyboard
        await callback.message.edit_text(
            text, 
            reply_markup=back_to_menu_keyboard(lang)
        )
        await callback.answer()
    
    elif item.type == 'system':
        # Системное действие
        await handle_system_action(callback, session, user, lang, item.system_action)
    
    elif item.type == 'faq':
        # FAQ - показать ответ
        from bot.models import FAQItem
        if item.value:
            faq_result = await session.execute(
                select(FAQItem).where(FAQItem.id == int(item.value))
            )
            faq = faq_result.scalar_one_or_none()
            if faq:
                answer = faq.answer_ru if lang == 'ru' else (faq.answer_en or faq.answer_ru)
                question = faq.question_ru if lang == 'ru' else (faq.question_en or faq.question_ru)
                
                from bot.keyboards import back_to_menu_keyboard
                await callback.message.edit_text(
                    f"❓ {question}\n\n{answer}",
                    reply_markup=back_to_menu_keyboard(lang)
                )
        await callback.answer()
    
    else:
        await callback.answer()


@router.callback_query(F.data.startswith("menu_back:"))
async def handle_menu_back(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    lang: str,
):
    """Вернуться на уровень выше."""
    parent_id = int(callback.data.split(":")[1])
    
    # Находим родителя текущего раздела
    result = await session.execute(
        select(MenuItem).where(MenuItem.id == parent_id)
    )
    item = result.scalar_one_or_none()
    
    if item:
        # Возвращаемся к родителю этого пункта
        await show_dynamic_menu(callback, session, user, lang, parent_id=item.parent_id)
    else:
        # Возвращаемся в корень
        await show_dynamic_menu(callback, session, user, lang, parent_id=None)


async def handle_system_action(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    lang: str,
    action: str
):
    """Обработка системных действий."""
    _ = lambda key: get_text(key, lang)
    
    if action == 'tariffs':
        # Показать тарифы
        from bot.models import Tariff
        from bot.keyboards import tariffs_keyboard
        
        result = await session.execute(
            select(Tariff).where(Tariff.is_active == True).order_by(Tariff.sort_order)
        )
        tariffs = result.scalars().all()
        
        await callback.message.edit_text(
            _('tariffs.title'),
            reply_markup=tariffs_keyboard(tariffs, lang)
        )
    
    elif action == 'subscriptions':
        # Мои подписки
        from bot.keyboards import subscriptions_keyboard, back_to_menu_keyboard
        
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
            await callback.message.edit_text(
                _('subscriptions.title'),
                reply_markup=subscriptions_keyboard(subscriptions, lang)
            )
    
    elif action == 'language':
        # Сменить язык
        from bot.keyboards import language_keyboard
        await callback.message.edit_text(
            _('choose_language'),
            reply_markup=language_keyboard()
        )
    
    elif action == 'support':
        # Поддержка
        from bot.keyboards import support_keyboard
        from bot.config import config
        await callback.message.edit_text(
            _('support.text'),
            reply_markup=support_keyboard(config.SUPPORT_URL, lang)
        )
    
    elif action == 'promocode':
        # Ввести промокод
        from bot.keyboards import back_to_menu_keyboard
        await callback.message.edit_text(
            _('promocode.enter'),
            reply_markup=back_to_menu_keyboard(lang)
        )
    
    await callback.answer()


# Обновляем callback для menu:main чтобы использовать динамическое меню
@router.callback_query(F.data == "menu:main")
async def menu_main_dynamic(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    lang: str,
):
    """Главное меню (динамическое)."""
    await show_dynamic_menu(callback, session, user, lang, parent_id=None)
