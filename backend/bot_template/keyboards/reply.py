"""
Reply клавиатуры (кнопки под полем ввода)
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """
    Главное меню бота.
    
    Returns:
        ReplyKeyboardMarkup с кнопками главного меню
    """
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📢 Каналы"),
                KeyboardButton(text="📋 Мои подписки")
            ],
            [
                KeyboardButton(text="🎁 Промокод"),
                KeyboardButton(text="💬 Поддержка")
            ]
        ],
        resize_keyboard=True,
        is_persistent=True
    )
    return keyboard


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """
    Клавиатура с кнопкой отмены.
    
    Returns:
        ReplyKeyboardMarkup с кнопкой отмены
    """
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❌ Отмена")]
        ],
        resize_keyboard=True
    )
    return keyboard
