"""
Хендлеры FAQ (вопросы-ответы).
"""

from typing import Callable, Optional

from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import User, FAQItem, MenuItem
from bot.locales import get_text

router = Router()


@router.callback_query(F.data.startswith("faq:"))
async def show_faq_answer(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    lang: str,
    _: Callable,
):
    """Показать ответ на FAQ вопрос."""
    faq_id = int(callback.data.split(':')[1])
    
    faq = await session.get(FAQItem, faq_id)
    
    if not faq:
        await callback.answer(_('error'), show_alert=True)
        return
    
    question = faq.get_question(lang)
    answer = faq.get_answer(lang)
    
    text = f"❓ <b>{question}</b>\n\n{answer}"
    
    # Определяем куда вернуться
    back_callback = "menu:main"
    if faq.category_id:
        # Возвращаемся к категории
        category = await session.get(MenuItem, faq.category_id)
        if category:
            back_callback = f"menu_faq:{category.id}"
    
    back_text = "◀️ Назад" if lang == "ru" else "◀️ Back"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=back_text, callback_data=back_callback)]
    ])
    
    await callback.message.edit_text(
        text,
        reply_markup=keyboard
    )
    await callback.answer()


async def get_all_faqs(
    session: AsyncSession,
    category_id: int | None = None,
) -> list[FAQItem]:
    """Получить все активные FAQ."""
    stmt = select(FAQItem).where(
        FAQItem.is_active == True,
    ).order_by(FAQItem.sort_order, FAQItem.id)
    
    if category_id is not None:
        stmt = stmt.where(FAQItem.category_id == category_id)
    
    result = await session.execute(stmt)
    return list(result.scalars().all())


def build_faq_keyboard(
    faqs: list[FAQItem],
    lang: str,
    back_callback: str = "menu:main",
) -> InlineKeyboardMarkup:
    """Построить клавиатуру FAQ."""
    builder = InlineKeyboardBuilder()
    
    for faq in faqs:
        question = faq.get_question(lang)
        # Обрезаем длинные вопросы
        if len(question) > 50:
            question = question[:47] + "..."
        
        builder.button(
            text=f"❓ {question}",
            callback_data=f"faq:{faq.id}"
        )
    
    back_text = "◀️ Назад" if lang == "ru" else "◀️ Back"
    builder.button(text=back_text, callback_data=back_callback)
    
    builder.adjust(1)
    return builder.as_markup()
