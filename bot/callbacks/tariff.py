"""
Callback-обработчики тарифов и покупки.
"""

from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import User, Tariff
from bot.keyboards import back_to_menu_keyboard
from bot.locales import get_text

router = Router()


@router.callback_query(F.data.startswith("buy:"))
async def buy_tariff(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    lang: str,
    _: callable,
):
    """Начать покупку тарифа."""
    tariff_id = int(callback.data.split(':')[1])
    
    # Получаем тариф
    tariff = await session.get(Tariff, tariff_id)
    
    if not tariff or not tariff.is_active:
        await callback.answer(_('error'), show_alert=True)
        return
    
    # Полная реализация оплаты в Чат 3
    # Пока показываем сообщение
    await callback.message.edit_text(
        _('payment.cryptobot_disabled'),
        reply_markup=back_to_menu_keyboard(lang)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("buy_trial:"))
async def buy_trial(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    lang: str,
    _: callable,
):
    """Активировать пробный период."""
    tariff_id = int(callback.data.split(':')[1])
    
    # Получаем тариф
    tariff = await session.get(Tariff, tariff_id)
    
    if not tariff or not tariff.is_active:
        await callback.answer(_('error'), show_alert=True)
        return
    
    # Полная реализация в Чат 5
    await callback.message.edit_text(
        "🎁 Пробный период будет реализован в Чат 5",
        reply_markup=back_to_menu_keyboard(lang)
    )
    await callback.answer()
