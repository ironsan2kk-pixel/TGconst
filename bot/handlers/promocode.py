"""
Хендлеры для работы с промокодами.
"""

from typing import Callable, Optional

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import User
from bot.locales import get_text
from bot.keyboards.inline import back_to_menu_keyboard
from bot.services.promocode import (
    validate_promocode,
    format_discount,
    PromocodeNotFoundError,
    PromocodeExpiredError,
    PromocodeAlreadyUsedError,
    PromocodeLimitReachedError,
)

router = Router()


class PromocodeStates(StatesGroup):
    """Состояния ввода промокода."""
    waiting_for_code = State()


@router.callback_query(F.data == "menu:promocode")
async def promocode_menu(
    callback: CallbackQuery,
    lang: str,
    _: Callable,
    state: FSMContext,
):
    """Меню ввода промокода."""
    await state.set_state(PromocodeStates.waiting_for_code)
    
    await callback.message.edit_text(
        _('promocode.enter'),
        reply_markup=back_to_menu_keyboard(lang)
    )
    await callback.answer()


@router.message(PromocodeStates.waiting_for_code)
async def process_promocode(
    message: Message,
    session: AsyncSession,
    user: User,
    lang: str,
    _: Callable,
    state: FSMContext,
):
    """Обработка введённого промокода."""
    code = message.text.strip().upper()
    
    try:
        promo, discount = await validate_promocode(
            session=session,
            code=code,
            user=user,
        )
        
        # Сохраняем промокод в состоянии для использования при оплате
        await state.update_data(active_promocode_id=promo.id)
        
        discount_str = format_discount(promo)
        
        await message.answer(
            _('promocode.applied').format(discount=discount_str),
            reply_markup=back_to_menu_keyboard(lang)
        )
        
    except PromocodeNotFoundError:
        await message.answer(
            _('promocode.invalid'),
            reply_markup=back_to_menu_keyboard(lang)
        )
    except PromocodeExpiredError:
        await message.answer(
            _('promocode.expired'),
            reply_markup=back_to_menu_keyboard(lang)
        )
    except PromocodeAlreadyUsedError:
        await message.answer(
            _('promocode.already_used'),
            reply_markup=back_to_menu_keyboard(lang)
        )
    except PromocodeLimitReachedError:
        await message.answer(
            _('promocode.limit_reached'),
            reply_markup=back_to_menu_keyboard(lang)
        )
    
    await state.clear()
