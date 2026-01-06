"""
Inline клавиатуры (кнопки в сообщениях)
"""
from typing import List, Optional
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ..database import get_active_channels


async def get_channels_keyboard() -> Optional[InlineKeyboardMarkup]:
    """
    Клавиатура со списком доступных каналов.
    
    Returns:
        InlineKeyboardMarkup или None если каналов нет
    """
    channels = await get_active_channels()
    
    if not channels:
        return None
    
    builder = InlineKeyboardBuilder()
    
    for channel in channels:
        builder.button(
            text=f"📢 {channel['title']}",
            callback_data=f"channel:{channel['id']}"
        )
    
    # По одной кнопке в ряд
    builder.adjust(1)
    
    return builder.as_markup()


def get_tariffs_keyboard(tariffs: List[dict], channel_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура со списком тарифов канала.
    
    Args:
        tariffs: Список тарифов
        channel_id: ID канала для кнопки "Назад"
    
    Returns:
        InlineKeyboardMarkup
    """
    builder = InlineKeyboardBuilder()
    
    for tariff in tariffs:
        # Форматируем срок
        days = tariff["duration_days"]
        if days == 30:
            duration = "1 мес"
        elif days == 90:
            duration = "3 мес"
        elif days == 180:
            duration = "6 мес"
        elif days == 365:
            duration = "1 год"
        else:
            duration = f"{days}д"
        
        # Форматируем цену
        price = tariff["price"]
        
        button_text = f"💳 {tariff['name']} — ${price:.2f} ({duration})"
        
        builder.button(
            text=button_text,
            callback_data=f"tariff:{tariff['id']}"
        )
    
    # Кнопка "Назад"
    builder.button(
        text="◀️ Назад к каналам",
        callback_data="back_to_channels"
    )
    
    # По одной кнопке в ряд
    builder.adjust(1)
    
    return builder.as_markup()


def get_payment_keyboard(tariff_id: int, channel_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура для оплаты тарифа.
    
    Args:
        tariff_id: ID тарифа
        channel_id: ID канала
        
    Returns:
        InlineKeyboardMarkup
    """
    builder = InlineKeyboardBuilder()
    
    # Кнопка "Применить промокод"
    builder.button(
        text="🎁 Ввести промокод",
        callback_data=f"promo:{tariff_id}:{channel_id}"
    )
    
    # Кнопка "Оплатить"
    builder.button(
        text="💳 Оплатить",
        callback_data=f"pay:{tariff_id}:{channel_id}"
    )
    
    # Кнопка "Назад"
    builder.button(
        text="◀️ Назад",
        callback_data=f"back_to_tariffs:{channel_id}"
    )
    
    # Промокод и Оплатить в один ряд, Назад отдельно
    builder.adjust(2, 1)
    
    return builder.as_markup()


def get_back_to_channels_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура с кнопкой возврата к каналам.
    
    Returns:
        InlineKeyboardMarkup
    """
    builder = InlineKeyboardBuilder()
    
    builder.button(
        text="◀️ Назад к каналам",
        callback_data="back_to_channels"
    )
    
    return builder.as_markup()


def get_confirm_payment_keyboard(invoice_url: str, payment_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура с кнопкой оплаты через CryptoBot.
    (Будет использоваться в Этапе 9)
    
    Args:
        invoice_url: URL для оплаты в CryptoBot
        payment_id: ID платежа в базе
        
    Returns:
        InlineKeyboardMarkup
    """
    builder = InlineKeyboardBuilder()
    
    # Кнопка ведущая на оплату в CryptoBot
    builder.button(
        text="💳 Оплатить в CryptoBot",
        url=invoice_url
    )
    
    # Кнопка проверки оплаты
    builder.button(
        text="🔄 Проверить оплату",
        callback_data=f"check_payment:{payment_id}"
    )
    
    # Кнопка отмены
    builder.button(
        text="❌ Отмена",
        callback_data="cancel_payment"
    )
    
    builder.adjust(1)
    
    return builder.as_markup()
