"""
Обработчик промокодов
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import Optional
import logging

from ..database import (
    validate_promocode,
    get_active_channels,
    get_user_by_telegram_id
)
from ..keyboards.reply import get_main_menu_keyboard

logger = logging.getLogger(__name__)

router = Router(name="promocode")


class PromoStates(StatesGroup):
    """Состояния для работы с промокодами"""
    waiting_code = State()


@router.message(F.text == "🎁 Промокод")
async def show_promocode_menu(message: Message, state: FSMContext):
    """
    Показать меню промокодов.
    Пользователь может ввести промокод и узнать скидку.
    """
    # Проверяем, есть ли уже активный промокод в state
    data = await state.get_data()
    current_promo = data.get("promocode")
    
    builder = InlineKeyboardBuilder()
    
    if current_promo:
        # Если промокод уже применён
        discount_text = ""
        if current_promo.get("discount_percent"):
            discount_text = f"{current_promo['discount_percent']}%"
        elif current_promo.get("discount_amount"):
            discount_text = f"${current_promo['discount_amount']:.2f}"
        
        text = (
            "🎁 <b>Промокод</b>\n\n"
            f"✅ У вас применён промокод: <code>{current_promo['code']}</code>\n"
            f"💰 Скидка: <b>{discount_text}</b>\n\n"
            "Скидка будет применена при следующей покупке."
        )
        
        builder.button(
            text="🗑 Удалить промокод",
            callback_data="promo_remove"
        )
        builder.button(
            text="🔄 Ввести другой",
            callback_data="promo_enter_new"
        )
        builder.adjust(1)
    else:
        text = (
            "🎁 <b>Промокод</b>\n\n"
            "Если у вас есть промокод, введите его для получения скидки.\n\n"
            "Скидка будет применена автоматически при следующей покупке."
        )
        
        builder.button(
            text="✏️ Ввести промокод",
            callback_data="promo_enter"
        )
        builder.adjust(1)
    
    await message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")


@router.callback_query(F.data == "promo_enter")
@router.callback_query(F.data == "promo_enter_new")
async def request_promocode_input(callback: CallbackQuery, state: FSMContext):
    """Запросить ввод промокода"""
    await callback.answer()
    await state.set_state(PromoStates.waiting_code)
    
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Отмена", callback_data="promo_cancel")
    
    await callback.message.edit_text(
        "🎁 <b>Ввод промокода</b>\n\n"
        "Отправьте промокод сообщением:",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "promo_cancel")
async def cancel_promocode_input(callback: CallbackQuery, state: FSMContext):
    """Отмена ввода промокода"""
    await callback.answer("Отменено")
    await state.set_state(None)
    
    await callback.message.edit_text(
        "🎁 Ввод промокода отменён.\n\n"
        "Вы можете ввести промокод позже."
    )


@router.callback_query(F.data == "promo_remove")
async def remove_promocode(callback: CallbackQuery, state: FSMContext):
    """Удалить применённый промокод"""
    await callback.answer("Промокод удалён")
    
    await state.update_data(
        promocode=None,
        discount=0,
        discount_percent=0,
        discount_amount=0
    )
    
    await callback.message.edit_text(
        "🗑 <b>Промокод удалён</b>\n\n"
        "Вы можете ввести новый промокод в любое время.",
        parse_mode="HTML"
    )


@router.message(PromoStates.waiting_code)
async def process_promocode_input(message: Message, state: FSMContext):
    """Обработка введённого промокода"""
    code = message.text.strip().upper()
    
    # Проверяем на команду отмены
    if code.startswith("/"):
        await state.set_state(None)
        await message.answer(
            "❌ Ввод промокода отменён.",
            reply_markup=get_main_menu_keyboard()
        )
        return
    
    # Валидируем промокод
    is_valid, promocode, error_msg = await validate_promocode(code)
    
    if not is_valid:
        builder = InlineKeyboardBuilder()
        builder.button(text="🔄 Попробовать снова", callback_data="promo_enter")
        builder.button(text="❌ Отмена", callback_data="promo_cancel")
        builder.adjust(1)
        
        await message.answer(
            f"❌ <b>Ошибка</b>\n\n{error_msg}\n\n"
            "Попробуйте ввести другой код.",
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )
        return
    
    # Промокод валидный - сохраняем
    await state.set_state(None)
    await state.update_data(
        promocode=promocode,
        discount_percent=promocode.get("discount_percent", 0),
        discount_amount=promocode.get("discount_amount", 0)
    )
    
    # Формируем описание скидки
    discount_text = ""
    if promocode.get("discount_percent"):
        discount_text = f"{promocode['discount_percent']}%"
    elif promocode.get("discount_amount"):
        discount_text = f"${promocode['discount_amount']:.2f}"
    
    # Информация о лимите
    limit_text = ""
    if promocode.get("max_uses"):
        remaining = promocode["max_uses"] - promocode.get("used_count", 0)
        limit_text = f"\n📊 Осталось использований: {remaining}"
    
    # Информация о сроке
    validity_text = ""
    if promocode.get("valid_until"):
        from datetime import datetime
        try:
            exp_date = datetime.fromisoformat(promocode["valid_until"])
            validity_text = f"\n⏰ Действует до: {exp_date.strftime('%d.%m.%Y')}"
        except:
            pass
    
    builder = InlineKeyboardBuilder()
    builder.button(text="📢 Выбрать канал", callback_data="back_to_channels")
    builder.button(text="🗑 Удалить промокод", callback_data="promo_remove")
    builder.adjust(1)
    
    await message.answer(
        f"✅ <b>Промокод применён!</b>\n\n"
        f"🎫 Код: <code>{code}</code>\n"
        f"💰 Скидка: <b>{discount_text}</b>{limit_text}{validity_text}\n\n"
        "Скидка будет автоматически применена при оплате.\n"
        "Выберите канал для покупки подписки!",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "promo_check")
async def check_current_promo(callback: CallbackQuery, state: FSMContext):
    """Проверить текущий промокод"""
    data = await state.get_data()
    current_promo = data.get("promocode")
    
    if not current_promo:
        await callback.answer("У вас нет активного промокода", show_alert=True)
        return
    
    # Переваливируем промокод (мог истечь)
    is_valid, _, error_msg = await validate_promocode(current_promo["code"])
    
    if not is_valid:
        await state.update_data(promocode=None, discount=0)
        await callback.answer(f"Промокод больше недействителен: {error_msg}", show_alert=True)
        return
    
    discount_text = ""
    if current_promo.get("discount_percent"):
        discount_text = f"{current_promo['discount_percent']}%"
    elif current_promo.get("discount_amount"):
        discount_text = f"${current_promo['discount_amount']:.2f}"
    
    await callback.answer(f"✅ Промокод: {current_promo['code']} (-{discount_text})", show_alert=True)


async def get_promo_discount(state: FSMContext, price: float) -> tuple[float, Optional[dict]]:
    """
    Получить скидку по промокоду из state.
    
    Args:
        state: FSMContext
        price: Исходная цена
        
    Returns:
        (discount_amount, promocode_data)
    """
    data = await state.get_data()
    promocode = data.get("promocode")
    
    if not promocode:
        return 0.0, None
    
    # Переваливируем на всякий случай
    is_valid, _, _ = await validate_promocode(promocode["code"])
    if not is_valid:
        return 0.0, None
    
    discount = 0.0
    if promocode.get("discount_percent"):
        discount = price * (promocode["discount_percent"] / 100)
    elif promocode.get("discount_amount"):
        discount = min(promocode["discount_amount"], price)
    
    return discount, promocode
