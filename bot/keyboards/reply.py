"""
Reply клавиатуры бота.
"""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from bot.locales import get_text


def main_reply_keyboard(lang: str) -> ReplyKeyboardMarkup:
    """Главная Reply клавиатура (всегда внизу)."""
    _ = lambda key: get_text(key, lang)
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=_('reply.get_access'))],
            [
                KeyboardButton(text=_('reply.my_subscriptions')),
                KeyboardButton(text=_('reply.settings'))
            ],
            [
                KeyboardButton(text=_('reply.contacts')),
                KeyboardButton(text=_('reply.promocode'))
            ],
        ],
        resize_keyboard=True,
        is_persistent=True
    )
    return keyboard


def remove_reply_keyboard() -> ReplyKeyboardRemove:
    """Убрать Reply клавиатуру."""
    return ReplyKeyboardRemove()
