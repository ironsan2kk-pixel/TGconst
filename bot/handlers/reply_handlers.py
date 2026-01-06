"""
Обработка Reply Keyboard нажатий.
"""

from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from bot.models import User, Subscription, Tariff, MenuItem, Channel
from bot.keyboards import tariffs_keyboard, back_to_menu_keyboard, main_reply_keyboard, dynamic_menu_keyboard
from bot.locales import get_text
from bot.config import config

router = Router()


# === Reply Keyboard Handlers ===

@router.message(F.text.in_(['🚀 Получить доступ', '🚀 Get access']))
async def reply_get_access(
    message: Message,
    session: AsyncSession,
    user: User,
    lang: str,
    _: callable,
):
    """Показать тарифы (Reply Keyboard)."""
    result = await session.execute(
        select(Tariff).where(Tariff.is_active == True).order_by(Tariff.sort_order)
    )
    tariffs = result.scalars().all()
    
    if not tariffs:
        await message.answer(_('tariffs.empty'))
        return
    
    await message.answer(
        _('tariffs.title'),
        reply_markup=tariffs_keyboard(tariffs, lang)
    )


@router.message(F.text.in_(['💳 Мои подписки', '💳 My subscriptions']))
async def reply_my_subscriptions(
    message: Message,
    session: AsyncSession,
    user: User,
    lang: str,
    _: callable,
):
    """Показать подписки пользователя (Reply Keyboard)."""
    result = await session.execute(
        select(Subscription)
        .where(
            Subscription.user_id == user.id,
            Subscription.is_active == True
        )
        .options(selectinload(Subscription.tariff))
    )
    subscriptions = result.scalars().all()
    
    # Проверка админа
    is_admin = user.telegram_id in config.ADMIN_IDS
    
    if not subscriptions and not is_admin:
        await message.answer(_('subscriptions.empty'))
        return
    
    text = _('subscriptions.title') + '\n'
    
    if is_admin:
        text += f"\n{_('admin.is_admin')}\n"
    
    for sub in subscriptions:
        tariff_name = sub.tariff.name_ru if lang == 'ru' else (sub.tariff.name_en or sub.tariff.name_ru)
        if sub.expires_at:
            expires = sub.expires_at.strftime('%d.%m.%Y')
            text += f"\n✅ <b>{tariff_name}</b>\n   До: {expires}"
        else:
            text += f"\n✅ <b>{tariff_name}</b>\n   Навсегда" if lang == 'ru' else f"\n✅ <b>{tariff_name}</b>\n   Forever"
    
    # Показываем каналы
    if subscriptions:
        text += f"\n\n📺 {'Каналы' if lang == 'ru' else 'Channels'}:"
        channels_shown = set()
        for sub in subscriptions:
            # Получаем каналы тарифа
            tariff_result = await session.execute(
                select(Tariff)
                .where(Tariff.id == sub.tariff_id)
                .options(selectinload(Tariff.channels))
            )
            tariff = tariff_result.scalar_one_or_none()
            if tariff:
                for channel in tariff.channels:
                    if channel.id not in channels_shown:
                        channels_shown.add(channel.id)
                        text += f"\n• @{channel.username}" if channel.username else f"\n• {channel.title}"
    
    await message.answer(text, parse_mode='HTML')


@router.message(F.text.in_(['⚙️ Настройки', '⚙️ Settings']))
async def reply_settings(
    message: Message,
    session: AsyncSession,
    user: User,
    lang: str,
    _: callable,
):
    """Показать настройки (Reply Keyboard)."""
    # Ищем раздел "Настройки" в меню
    result = await session.execute(
        select(MenuItem).where(
            MenuItem.is_active == True,
            MenuItem.parent_id == None,
            MenuItem.type == 'section'
        ).order_by(MenuItem.sort_order)
    )
    items = result.scalars().all()
    
    # Ищем раздел настроек по тексту
    settings_section = None
    for item in items:
        if 'настройки' in item.text_ru.lower() or 'settings' in (item.text_en or '').lower():
            settings_section = item
            break
    
    if settings_section:
        # Получаем дочерние элементы
        children_result = await session.execute(
            select(MenuItem).where(
                MenuItem.parent_id == settings_section.id,
                MenuItem.is_active == True
            ).order_by(MenuItem.sort_order)
        )
        children = children_result.scalars().all()
        
        if children:
            await message.answer(
                _('settings.title'),
                reply_markup=dynamic_menu_keyboard(children, lang, settings_section.id)
            )
            return
    
    # Если нет настроек в БД - показываем заглушку
    await message.answer(_('settings.title'))


@router.message(F.text.in_(['📞 Контакты', '📞 Contacts']))
async def reply_contacts(
    message: Message,
    session: AsyncSession,
    user: User,
    lang: str,
    _: callable,
):
    """Показать контакты (Reply Keyboard)."""
    # Ищем пункт "Контакты" в меню
    result = await session.execute(
        select(MenuItem).where(
            MenuItem.is_active == True,
            MenuItem.parent_id == None,
            MenuItem.type == 'text'
        )
    )
    items = result.scalars().all()
    
    # Ищем контакты по тексту
    contacts_item = None
    for item in items:
        if 'контакт' in item.text_ru.lower() or 'contact' in (item.text_en or '').lower():
            contacts_item = item
            break
    
    if contacts_item and contacts_item.value:
        text = contacts_item.value
        
        # Отправляем с фото если есть
        if contacts_item.photo_file_id:
            await message.answer_photo(
                photo=contacts_item.photo_file_id,
                caption=text,
                parse_mode='HTML'
            )
        else:
            await message.answer(text, parse_mode='HTML')
        return
    
    # Заглушка
    text = _('contacts.title')
    if config.SUPPORT_URL:
        text += f"\n\nSupport: {config.SUPPORT_URL}"
    await message.answer(text)


@router.message(F.text.in_(['🎁 Промокод', '🎁 Promocode']))
async def reply_promocode(
    message: Message,
    session: AsyncSession,
    user: User,
    lang: str,
    _: callable,
):
    """Показать ввод промокода (Reply Keyboard)."""
    await message.answer(_('promocode.enter'))
