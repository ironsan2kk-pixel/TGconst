"""
Клавиатуры бота.
"""

from bot.keyboards.inline import (
    language_keyboard,
    main_menu_keyboard,
    tariffs_keyboard,
    tariff_detail_keyboard,
    back_to_menu_keyboard,
    payment_keyboard,
    support_keyboard,
    dynamic_menu_keyboard,
)

from bot.keyboards.reply import (
    main_reply_keyboard,
    remove_reply_keyboard,
)


__all__ = [
    # Inline
    'language_keyboard',
    'main_menu_keyboard',
    'tariffs_keyboard',
    'tariff_detail_keyboard',
    'back_to_menu_keyboard',
    'payment_keyboard',
    'support_keyboard',
    'dynamic_menu_keyboard',
    # Reply
    'main_reply_keyboard',
    'remove_reply_keyboard',
]
