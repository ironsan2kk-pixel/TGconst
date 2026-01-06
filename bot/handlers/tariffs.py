"""
Обработка тарифов.
"""

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from bot.models import User, Tariff, TariffChannel, Channel, Subscription
from bot.keyboards import tariffs_keyboard, tariff_detail_keyboard, back_to_menu_keyboard
from bot.locales import get_text

router = Router()


async def get_active_tariffs(session: AsyncSession) -> list[Tariff]:
    """Получить активные тарифы."""
    result = await session.execute(
        select(Tariff)
        .where(Tariff.is_active == True)
        .order_by(Tariff.sort_order, Tariff.id)
    )
    return result.scalars().all()


async def get_tariff_with_channels(
    session: AsyncSession, 
    tariff_id: int
) -> tuple[Tariff | None, list[Channel]]:
    """Получить тариф с его каналами."""
    result = await session.execute(
        select(Tariff).where(Tariff.id == tariff_id)
    )
    tariff = result.scalar_one_or_none()
    
    if not tariff:
        return None, []
    
    # Получаем каналы тарифа
    result = await session.execute(
        select(Channel)
        .join(TariffChannel, TariffChannel.channel_id == Channel.id)
        .where(TariffChannel.tariff_id == tariff_id)
        .where(Channel.is_active == True)
    )
    channels = result.scalars().all()
    
    return tariff, channels


async def user_has_trial_used(
    session: AsyncSession, 
    user_id: int, 
    tariff_id: int
) -> bool:
    """Проверить, использовал ли юзер пробный период для этого тарифа."""
    result = await session.execute(
        select(Subscription).where(
            Subscription.user_id == user_id,
            Subscription.tariff_id == tariff_id,
            Subscription.is_trial == True
        )
    )
    return result.scalar_one_or_none() is not None


@router.message(Command('tariffs'))
async def cmd_tariffs(
    message: Message,
    session: AsyncSession,
    lang: str,
    _: callable,
):
    """Команда /tariffs."""
    tariffs = await get_active_tariffs(session)
    
    if not tariffs:
        await message.answer(
            _('tariffs.empty'),
            reply_markup=back_to_menu_keyboard(lang)
        )
        return
    
    await message.answer(
        _('tariffs.title'),
        reply_markup=tariffs_keyboard(tariffs, lang)
    )


@router.callback_query(F.data == "menu:tariffs")
async def callback_tariffs(
    callback: CallbackQuery,
    session: AsyncSession,
    lang: str,
    _: callable,
):
    """Показать список тарифов из меню."""
    tariffs = await get_active_tariffs(session)
    
    if not tariffs:
        await callback.message.edit_text(
            _('tariffs.empty'),
            reply_markup=back_to_menu_keyboard(lang)
        )
        await callback.answer()
        return
    
    await callback.message.edit_text(
        _('tariffs.title'),
        reply_markup=tariffs_keyboard(tariffs, lang)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("tariff:"))
async def callback_tariff_detail(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    lang: str,
    _: callable,
):
    """Показать детали тарифа."""
    tariff_id = int(callback.data.split(':')[1])
    await show_tariff_detail(callback.message, session, user, lang, _, tariff_id, edit=True)
    await callback.answer()


async def show_tariff_detail(
    message: Message,
    session: AsyncSession,
    user: User,
    lang: str,
    _: callable,
    tariff_id: int,
    edit: bool = False,
):
    """Показать детали тарифа (используется и для deep link и для callback)."""
    tariff, channels = await get_tariff_with_channels(session, tariff_id)
    
    if not tariff or not tariff.is_active:
        text = _('error')
        keyboard = back_to_menu_keyboard(lang)
        
        if edit:
            await message.edit_text(text, reply_markup=keyboard)
        else:
            await message.answer(text, reply_markup=keyboard)
        return
    
    # Название и описание на нужном языке
    name = tariff.name_ru if lang == 'ru' else (tariff.name_en or tariff.name_ru)
    description = tariff.description_ru if lang == 'ru' else (tariff.description_en or tariff.description_ru or '')
    
    # Формат длительности
    if tariff.duration_days == 0:
        duration = _('tariffs.duration_forever')
    else:
        duration = _('tariffs.duration_days', days=tariff.duration_days)
    
    # Пробный период
    trial_text = ''
    if tariff.trial_days and tariff.trial_days > 0:
        trial_text = _('tariffs.trial_info', days=tariff.trial_days)
    
    # Список каналов
    if channels:
        channels_text = '\n'.join([f"• {ch.title or ch.username}" for ch in channels])
    else:
        channels_text = '—'
    
    # Формируем текст
    text = _('tariffs.detail',
             name=name,
             description=description,
             price=f"{tariff.price:.2f}",
             duration=duration,
             trial=trial_text,
             channels=channels_text)
    
    # Проверяем, использован ли trial
    trial_available = False
    if tariff.trial_days and tariff.trial_days > 0:
        trial_used = await user_has_trial_used(session, user.id, tariff_id)
        trial_available = not trial_used
    
    keyboard = tariff_detail_keyboard(tariff, lang, has_trial=trial_available)
    
    if edit:
        await message.edit_text(text, reply_markup=keyboard)
    else:
        await message.answer(text, reply_markup=keyboard)
