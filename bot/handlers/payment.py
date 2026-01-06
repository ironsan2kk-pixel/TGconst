"""
Хендлеры для процесса оплаты.
"""

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import User, Payment
from bot.keyboards import main_menu_keyboard

router = Router()


# Здесь будут хендлеры для ввода промокода при оплате и т.д.
# Основная логика оплаты в callbacks/payment.py
