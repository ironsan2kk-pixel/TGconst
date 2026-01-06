"""
Клавиатуры бота
"""
from .reply import get_main_menu_keyboard
from .inline import (
    get_channels_keyboard,
    get_tariffs_keyboard,
    get_payment_keyboard,
    get_back_to_channels_keyboard
)

__all__ = [
    "get_main_menu_keyboard",
    "get_channels_keyboard",
    "get_tariffs_keyboard",
    "get_payment_keyboard",
    "get_back_to_channels_keyboard"
]
