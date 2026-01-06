"""
Обработчик команды /start
"""
from typing import Any, Dict
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart

from ..database import get_or_create_user
from ..keyboards.reply import get_main_menu_keyboard

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message, bot_config: Dict[str, Any] = None):
    """Обработка команды /start"""
    # Получаем или создаём пользователя в базе
    user = await get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )
    
    # Получаем приветственное сообщение из конфига бота
    bot_config = bot_config or {}
    welcome_text = bot_config.get("welcome_message", "👋 Добро пожаловать!")
    
    # Форматируем сообщение
    name = message.from_user.first_name or "друг"
    text = f"{welcome_text}\n\n{name}, выберите действие в меню ниже 👇"
    
    await message.answer(
        text,
        reply_markup=get_main_menu_keyboard()
    )
