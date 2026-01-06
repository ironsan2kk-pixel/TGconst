"""
Хендлеры навигации по динамическому меню.

Обрабатывает элементы меню из конструктора (MenuItem).
"""

from typing import Callable, Optional

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bot.models import User, MenuItem, FAQItem
from bot.locales import get_text
from bot.services.subscription import get_user_subscriptions

router = Router()


async def get_menu_items(
    session: AsyncSession,
    parent_id: int | None = None,
    user: User | None = None,
    lang: str = "ru",
) -> list[MenuItem]:
    """
    Получить элементы меню для отображения.
    
    Args:
        session: Сессия БД
        parent_id: ID родительского элемента (None = корень)
        user: Пользователь (для проверки условий видимости)
        lang: Язык пользователя
        
    Returns:
        Список отфильтрованных элементов меню
    """
    stmt = select(MenuItem).where(
        MenuItem.parent_id == parent_id,
        MenuItem.is_active == True,
    ).order_by(MenuItem.sort_order, MenuItem.id)
    
    result = await session.execute(stmt)
    items = result.scalars().all()
    
    # Фильтруем по условиям видимости
    filtered_items = []
    
    # Проверяем есть ли подписка
    has_subscription = False
    if user:
        subscriptions = await get_user_subscriptions(session, user.id, active_only=True)
        has_subscription = len(subscriptions) > 0
    
    for item in items:
        # Проверяем видимость по языку
        if item.visibility_language != "all" and item.visibility_language != lang:
            continue
        
        # Проверяем видимость по подписке
        if item.visibility == "subscribed" and not has_subscription:
            continue
        if item.visibility == "not_subscribed" and has_subscription:
            continue
        
        filtered_items.append(item)
    
    return filtered_items


def build_menu_keyboard(
    items: list[MenuItem],
    parent_id: int | None = None,
    lang: str = "ru",
) -> InlineKeyboardMarkup:
    """Построить клавиатуру меню."""
    builder = InlineKeyboardBuilder()
    
    for item in items:
        text = item.get_button_text(lang)
        
        if item.type == "section":
            # Раздел - открывает подменю
            callback_data = f"menu_item:{item.id}"
        elif item.type == "link":
            # Внешняя ссылка
            builder.button(text=text, url=item.value or "")
            continue
        elif item.type == "text":
            # Отправляет текстовое сообщение
            callback_data = f"menu_text:{item.id}"
        elif item.type == "faq":
            # Показывает FAQ
            callback_data = f"menu_faq:{item.id}"
        elif item.type == "system":
            # Системное действие
            callback_data = f"menu:{item.system_action}"
        else:
            continue
        
        builder.button(text=text, callback_data=callback_data)
    
    # Кнопка "Назад" если это подменю
    if parent_id is not None:
        # Получаем родителя для определения куда идти назад
        back_text = "◀️ Назад" if lang == "ru" else "◀️ Back"
        builder.button(text=back_text, callback_data=f"menu_back:{parent_id}")
    
    builder.adjust(1)
    return builder.as_markup()


@router.callback_query(F.data.startswith("menu_item:"))
async def show_submenu(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    lang: str,
    _: Callable,
):
    """Показать подменю (раздел)."""
    item_id = int(callback.data.split(':')[1])
    
    # Получаем элемент меню
    item = await session.get(MenuItem, item_id)
    
    if not item:
        await callback.answer(_('error'), show_alert=True)
        return
    
    # Получаем дочерние элементы
    children = await get_menu_items(
        session=session,
        parent_id=item.id,
        user=user,
        lang=lang,
    )
    
    if not children:
        await callback.answer("Раздел пуст" if lang == "ru" else "Section is empty", show_alert=True)
        return
    
    title = item.get_button_text(lang)
    
    await callback.message.edit_text(
        f"📁 <b>{title}</b>",
        reply_markup=build_menu_keyboard(children, item.id, lang)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("menu_back:"))
async def go_back(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    lang: str,
    _: Callable,
):
    """Вернуться на уровень выше в меню."""
    parent_id = int(callback.data.split(':')[1])
    
    # Получаем родительский элемент
    parent = await session.get(MenuItem, parent_id)
    
    if parent and parent.parent_id is not None:
        # У родителя тоже есть родитель - показываем siblings родителя
        grandparent_id = parent.parent_id
        items = await get_menu_items(
            session=session,
            parent_id=grandparent_id,
            user=user,
            lang=lang,
        )
        
        grandparent = await session.get(MenuItem, grandparent_id)
        title = grandparent.get_button_text(lang) if grandparent else _('menu.title')
        
        await callback.message.edit_text(
            f"📁 <b>{title}</b>",
            reply_markup=build_menu_keyboard(items, grandparent_id, lang)
        )
    else:
        # Возвращаемся в главное меню
        from bot.keyboards.inline import main_menu_keyboard
        
        subscriptions = await get_user_subscriptions(session, user.id, active_only=True)
        has_subscription = len(subscriptions) > 0
        
        await callback.message.edit_text(
            _('menu.title'),
            reply_markup=main_menu_keyboard(lang, has_subscription)
        )
    
    await callback.answer()


@router.callback_query(F.data.startswith("menu_text:"))
async def show_text_item(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    lang: str,
    _: Callable,
):
    """Показать текстовое сообщение из элемента меню (с фото если есть)."""
    item_id = int(callback.data.split(':')[1])
    
    item = await session.get(MenuItem, item_id)
    
    if not item or not item.value:
        await callback.answer(_('error'), show_alert=True)
        return
    
    # Кнопка назад
    back_text = "◀️ Назад" if lang == "ru" else "◀️ Back"
    parent_id = item.parent_id or 0
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=back_text,
            callback_data=f"menu_back:{parent_id}" if parent_id else "menu:main"
        )]
    ])
    
    # Если есть фото - отправляем новым сообщением (edit_text не умеет в фото)
    if item.photo_file_id:
        # Удаляем старое сообщение и отправляем новое с фото
        await callback.message.delete()
        await callback.message.answer_photo(
            photo=item.photo_file_id,
            caption=item.value,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
    else:
        await callback.message.edit_text(
            item.value,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
    await callback.answer()


@router.callback_query(F.data.startswith("menu_faq:"))
async def show_faq_from_menu(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    lang: str,
    _: Callable,
):
    """Показать FAQ из элемента меню."""
    item_id = int(callback.data.split(':')[1])
    
    item = await session.get(MenuItem, item_id)
    
    if not item:
        await callback.answer(_('error'), show_alert=True)
        return
    
    # Если value содержит ID FAQ
    if item.value and item.value.isdigit():
        faq_id = int(item.value)
        faq = await session.get(FAQItem, faq_id)
        
        if faq:
            text = f"❓ <b>{faq.get_question(lang)}</b>\n\n{faq.get_answer(lang)}"
        else:
            text = "FAQ не найден" if lang == "ru" else "FAQ not found"
    else:
        # Показываем все FAQ в категории
        stmt = select(FAQItem).where(
            FAQItem.category_id == item.id,
            FAQItem.is_active == True,
        ).order_by(FAQItem.sort_order)
        
        result = await session.execute(stmt)
        faqs = result.scalars().all()
        
        if faqs:
            # Строим клавиатуру с вопросами
            builder = InlineKeyboardBuilder()
            for faq in faqs:
                builder.button(
                    text=f"❓ {faq.get_question(lang)[:50]}...",
                    callback_data=f"faq:{faq.id}"
                )
            
            back_text = "◀️ Назад" if lang == "ru" else "◀️ Back"
            parent_id = item.parent_id or 0
            builder.button(
                text=back_text,
                callback_data=f"menu_back:{parent_id}" if parent_id else "menu:main"
            )
            builder.adjust(1)
            
            title = item.get_button_text(lang)
            await callback.message.edit_text(
                f"📁 <b>{title}</b>\n\n"
                f"{'Выберите вопрос:' if lang == 'ru' else 'Select a question:'}",
                reply_markup=builder.as_markup()
            )
            await callback.answer()
            return
        else:
            text = "Вопросов пока нет" if lang == "ru" else "No questions yet"
    
    # Кнопка назад
    back_text = "◀️ Назад" if lang == "ru" else "◀️ Back"
    parent_id = item.parent_id or 0
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=back_text,
            callback_data=f"menu_back:{parent_id}" if parent_id else "menu:main"
        )]
    ])
    
    await callback.message.edit_text(
        text,
        reply_markup=keyboard
    )
    await callback.answer()


