"""
Хендлеры админ-панели в Telegram боте.

Команды /admin и /stats доступны только админам.
"""

import json
from datetime import datetime, timedelta

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bot.config import config
from bot.models import (
    User, Tariff, TariffChannel, Subscription, Payment, 
    Promocode, AdminLog, Channel
)
from bot.locales import get_text
from bot.services.subscription import create_subscription, get_tariff_channels

router = Router()


class AdminStates(StatesGroup):
    """Состояния админки."""
    search_user = State()
    grant_access_user_id = State()
    grant_access_tariff = State()
    revoke_access_user_id = State()
    ban_user_id = State()
    ban_reason = State()
    unban_user_id = State()
    manual_payment_user_id = State()
    manual_payment_tariff = State()
    broadcast_text = State()


def is_admin(user_id: int) -> bool:
    """Проверить, является ли пользователь админом."""
    return user_id in config.ADMIN_IDS


def admin_menu_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура админ-меню."""
    buttons = [
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin:stats")],
        [InlineKeyboardButton(text="🔍 Найти юзера", callback_data="admin:search")],
        [
            InlineKeyboardButton(text="➕ Выдать доступ", callback_data="admin:grant"),
            InlineKeyboardButton(text="➖ Забрать", callback_data="admin:revoke"),
        ],
        [
            InlineKeyboardButton(text="🚫 Забанить", callback_data="admin:ban"),
            InlineKeyboardButton(text="✅ Разбанить", callback_data="admin:unban"),
        ],
        [InlineKeyboardButton(text="💳 Ручная оплата", callback_data="admin:manual_payment")],
        [InlineKeyboardButton(text="📨 Рассылка", callback_data="admin:broadcast")],
        [InlineKeyboardButton(text="❌ Закрыть", callback_data="admin:close")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def back_to_admin_keyboard() -> InlineKeyboardMarkup:
    """Кнопка возврата в админку."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin:menu")]
    ])


async def log_admin_action(
    session: AsyncSession,
    admin_telegram_id: int,
    action: str,
    target_user_id: int | None = None,
    details: dict | None = None,
):
    """Записать действие админа в лог."""
    log = AdminLog(
        admin_telegram_id=admin_telegram_id,
        action=action,
        target_user_id=target_user_id,
        details=json.dumps(details) if details else None,
    )
    session.add(log)
    await session.commit()


@router.message(Command("admin"))
async def cmd_admin(
    message: Message,
    user: User,
):
    """Команда /admin — открыть админ-меню."""
    if not is_admin(message.from_user.id):
        await message.answer("⛔ У вас нет доступа к админ-панели.")
        return
    
    await message.answer(
        "🔧 <b>Админ-панель</b>\n\n"
        "Выберите действие:",
        reply_markup=admin_menu_keyboard()
    )


@router.message(Command("stats"))
async def cmd_stats(
    message: Message,
    session: AsyncSession,
):
    """Команда /stats — быстрая статистика."""
    if not is_admin(message.from_user.id):
        await message.answer("⛔ У вас нет доступа.")
        return
    
    # Считаем статистику
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Всего юзеров
    total_users = await session.scalar(select(func.count(User.id)))
    
    # Активные подписки
    active_subs = await session.scalar(
        select(func.count(Subscription.id)).where(
            Subscription.is_active == True,
            (Subscription.expires_at == None) | (Subscription.expires_at > now)
        )
    )
    
    # Доход сегодня
    today_revenue = await session.scalar(
        select(func.coalesce(func.sum(Payment.amount), 0)).where(
            Payment.status == "paid",
            Payment.paid_at >= today_start,
        )
    ) or 0
    
    # Доход за месяц
    month_revenue = await session.scalar(
        select(func.coalesce(func.sum(Payment.amount), 0)).where(
            Payment.status == "paid",
            Payment.paid_at >= month_start,
        )
    ) or 0
    
    # Новые юзеры сегодня
    new_users_today = await session.scalar(
        select(func.count(User.id)).where(
            User.created_at >= today_start
        )
    )
    
    text = (
        "📊 <b>Статистика</b>\n\n"
        f"👥 Всего пользователей: <b>{total_users}</b>\n"
        f"📈 Новых сегодня: <b>{new_users_today}</b>\n\n"
        f"✅ Активных подписок: <b>{active_subs}</b>\n\n"
        f"💰 Доход сегодня: <b>{today_revenue:.2f} USDT</b>\n"
        f"💰 Доход за месяц: <b>{month_revenue:.2f} USDT</b>"
    )
    
    await message.answer(text, reply_markup=back_to_admin_keyboard())


@router.callback_query(F.data == "admin:menu")
async def admin_menu(callback: CallbackQuery, state: FSMContext):
    """Вернуться в админ-меню."""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return
    
    await state.clear()
    
    await callback.message.edit_text(
        "🔧 <b>Админ-панель</b>\n\n"
        "Выберите действие:",
        reply_markup=admin_menu_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "admin:stats")
async def admin_stats(
    callback: CallbackQuery,
    session: AsyncSession,
):
    """Показать статистику."""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return
    
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    total_users = await session.scalar(select(func.count(User.id)))
    
    active_subs = await session.scalar(
        select(func.count(Subscription.id)).where(
            Subscription.is_active == True,
            (Subscription.expires_at == None) | (Subscription.expires_at > now)
        )
    )
    
    today_revenue = await session.scalar(
        select(func.coalesce(func.sum(Payment.amount), 0)).where(
            Payment.status == "paid",
            Payment.paid_at >= today_start,
        )
    ) or 0
    
    month_revenue = await session.scalar(
        select(func.coalesce(func.sum(Payment.amount), 0)).where(
            Payment.status == "paid",
            Payment.paid_at >= month_start,
        )
    ) or 0
    
    new_users_today = await session.scalar(
        select(func.count(User.id)).where(User.created_at >= today_start)
    )
    
    text = (
        "📊 <b>Статистика</b>\n\n"
        f"👥 Всего пользователей: <b>{total_users}</b>\n"
        f"📈 Новых сегодня: <b>{new_users_today}</b>\n\n"
        f"✅ Активных подписок: <b>{active_subs}</b>\n\n"
        f"💰 Доход сегодня: <b>{today_revenue:.2f} USDT</b>\n"
        f"💰 Доход за месяц: <b>{month_revenue:.2f} USDT</b>"
    )
    
    await callback.message.edit_text(text, reply_markup=back_to_admin_keyboard())
    await callback.answer()


@router.callback_query(F.data == "admin:search")
async def admin_search_start(callback: CallbackQuery, state: FSMContext):
    """Начать поиск юзера."""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return
    
    await state.set_state(AdminStates.search_user)
    
    await callback.message.edit_text(
        "🔍 <b>Поиск пользователя</b>\n\n"
        "Введите Telegram ID или @username:",
        reply_markup=back_to_admin_keyboard()
    )
    await callback.answer()


@router.message(AdminStates.search_user)
async def admin_search_process(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
):
    """Обработка поиска юзера."""
    query = message.text.strip()
    
    # Ищем по telegram_id или username
    if query.startswith('@'):
        username = query[1:]
        stmt = select(User).where(User.username == username)
    elif query.isdigit():
        stmt = select(User).where(User.telegram_id == int(query))
    else:
        stmt = select(User).where(User.username == query)
    
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        await message.answer(
            "❌ Пользователь не найден.",
            reply_markup=back_to_admin_keyboard()
        )
        await state.clear()
        return
    
    # Получаем подписки
    stmt = select(Subscription).where(
        Subscription.user_id == user.id,
        Subscription.is_active == True,
    ).options(selectinload(Subscription.tariff))
    
    result = await session.execute(stmt)
    subscriptions = result.scalars().all()
    
    subs_text = ""
    if subscriptions:
        for sub in subscriptions:
            expires = sub.expires_at.strftime('%d.%m.%Y') if sub.expires_at else "∞"
            subs_text += f"\n  • {sub.tariff.name_ru} (до {expires})"
    else:
        subs_text = "\n  Нет активных подписок"
    
    text = (
        f"👤 <b>Пользователь</b>\n\n"
        f"ID: <code>{user.telegram_id}</code>\n"
        f"Имя: {user.first_name or '-'}\n"
        f"Username: @{user.username or '-'}\n"
        f"Язык: {user.language}\n"
        f"Забанен: {'Да' if user.is_banned else 'Нет'}\n"
        f"Регистрация: {user.created_at.strftime('%d.%m.%Y %H:%M')}\n"
        f"\n📋 Подписки:{subs_text}"
    )
    
    buttons = [
        [
            InlineKeyboardButton(text="➕ Выдать доступ", callback_data=f"admin:grant_user:{user.id}"),
            InlineKeyboardButton(text="➖ Забрать", callback_data=f"admin:revoke_user:{user.id}"),
        ],
    ]
    
    if user.is_banned:
        buttons.append([InlineKeyboardButton(text="✅ Разбанить", callback_data=f"admin:unban_user:{user.id}")])
    else:
        buttons.append([InlineKeyboardButton(text="🚫 Забанить", callback_data=f"admin:ban_user:{user.id}")])
    
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="admin:menu")])
    
    await message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await state.clear()


@router.callback_query(F.data == "admin:grant")
async def admin_grant_start(callback: CallbackQuery, state: FSMContext):
    """Начать выдачу доступа."""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return
    
    await state.set_state(AdminStates.grant_access_user_id)
    
    await callback.message.edit_text(
        "➕ <b>Выдача доступа</b>\n\n"
        "Введите Telegram ID или @username пользователя:",
        reply_markup=back_to_admin_keyboard()
    )
    await callback.answer()


@router.message(AdminStates.grant_access_user_id)
async def admin_grant_user(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
):
    """Обработка ввода юзера для выдачи доступа."""
    query = message.text.strip()
    
    if query.startswith('@'):
        username = query[1:]
        stmt = select(User).where(User.username == username)
    elif query.isdigit():
        stmt = select(User).where(User.telegram_id == int(query))
    else:
        stmt = select(User).where(User.username == query)
    
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        await message.answer(
            "❌ Пользователь не найден.",
            reply_markup=back_to_admin_keyboard()
        )
        await state.clear()
        return
    
    await state.update_data(target_user_id=user.id)
    await state.set_state(AdminStates.grant_access_tariff)
    
    # Показываем тарифы
    stmt = select(Tariff).where(Tariff.is_active == True).order_by(Tariff.sort_order)
    result = await session.execute(stmt)
    tariffs = result.scalars().all()
    
    if not tariffs:
        await message.answer(
            "❌ Нет активных тарифов.",
            reply_markup=back_to_admin_keyboard()
        )
        await state.clear()
        return
    
    buttons = []
    for tariff in tariffs:
        buttons.append([InlineKeyboardButton(
            text=f"{tariff.name_ru} ({tariff.price} USDT)",
            callback_data=f"admin:grant_tariff:{tariff.id}"
        )])
    buttons.append([InlineKeyboardButton(text="◀️ Отмена", callback_data="admin:menu")])
    
    await message.answer(
        f"👤 Пользователь: {user.first_name} (@{user.username})\n\n"
        "Выберите тариф:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )


@router.callback_query(F.data.startswith("admin:grant_tariff:"))
async def admin_grant_execute(
    callback: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    bot: Bot,
):
    """Выполнить выдачу доступа."""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return
    
    tariff_id = int(callback.data.split(':')[2])
    data = await state.get_data()
    target_user_id = data.get('target_user_id')
    
    if not target_user_id:
        await callback.answer("Ошибка: пользователь не выбран", show_alert=True)
        await state.clear()
        return
    
    # Получаем юзера и тариф
    user = await session.get(User, target_user_id)
    tariff = await session.get(Tariff, tariff_id, options=[
        selectinload(Tariff.tariff_channels).selectinload(TariffChannel.channel)
    ])
    
    if not user or not tariff:
        await callback.answer("Ошибка", show_alert=True)
        await state.clear()
        return
    
    # Создаём подписку
    subscription = await create_subscription(
        session=session,
        user=user,
        tariff=tariff,
        granted_by=callback.from_user.id,
    )
    
    # Логируем действие
    await log_admin_action(
        session=session,
        admin_telegram_id=callback.from_user.id,
        action="grant_access",
        target_user_id=user.id,
        details={"tariff_id": tariff.id, "subscription_id": subscription.id},
    )
    
    # Уведомляем юзера
    try:
        channels = await get_tariff_channels(session, tariff)
        
        if subscription.expires_at:
            expires = subscription.expires_at.strftime('%d.%m.%Y')
            user_text = (
                f"🎉 <b>Вам выдан доступ!</b>\n\n"
                f"📦 Тариф: {tariff.name_ru}\n"
                f"⏱ Активен до: {expires}\n\n"
                f"🔗 Ссылки на каналы:"
            )
        else:
            user_text = (
                f"🎉 <b>Вам выдан доступ!</b>\n\n"
                f"📦 Тариф: {tariff.name_ru}\n"
                f"⏱ Срок: Навсегда\n\n"
                f"🔗 Ссылки на каналы:"
            )
        
        await bot.send_message(user.telegram_id, user_text)
        
        for channel in channels:
            if channel.invite_link:
                await bot.send_message(
                    user.telegram_id,
                    f"📺 {channel.title}: {channel.invite_link}"
                )
    except Exception as e:
        pass  # Юзер мог заблокировать бота
    
    await callback.message.edit_text(
        f"✅ <b>Доступ выдан!</b>\n\n"
        f"Пользователь: {user.first_name} (@{user.username})\n"
        f"Тариф: {tariff.name_ru}",
        reply_markup=back_to_admin_keyboard()
    )
    await state.clear()
    await callback.answer()


@router.callback_query(F.data.startswith("admin:grant_user:"))
async def admin_grant_user_direct(
    callback: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
):
    """Выдать доступ конкретному юзеру (из поиска)."""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return
    
    user_id = int(callback.data.split(':')[2])
    await state.update_data(target_user_id=user_id)
    await state.set_state(AdminStates.grant_access_tariff)
    
    user = await session.get(User, user_id)
    
    stmt = select(Tariff).where(Tariff.is_active == True).order_by(Tariff.sort_order)
    result = await session.execute(stmt)
    tariffs = result.scalars().all()
    
    buttons = []
    for tariff in tariffs:
        buttons.append([InlineKeyboardButton(
            text=f"{tariff.name_ru} ({tariff.price} USDT)",
            callback_data=f"admin:grant_tariff:{tariff.id}"
        )])
    buttons.append([InlineKeyboardButton(text="◀️ Отмена", callback_data="admin:menu")])
    
    await callback.message.edit_text(
        f"👤 Пользователь: {user.first_name} (@{user.username})\n\n"
        "Выберите тариф:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )
    await callback.answer()


@router.callback_query(F.data == "admin:revoke")
async def admin_revoke_start(callback: CallbackQuery, state: FSMContext):
    """Начать отзыв доступа."""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return
    
    await state.set_state(AdminStates.revoke_access_user_id)
    
    await callback.message.edit_text(
        "➖ <b>Отзыв доступа</b>\n\n"
        "Введите Telegram ID или @username пользователя:",
        reply_markup=back_to_admin_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:revoke_user:"))
async def admin_revoke_user_direct(
    callback: CallbackQuery,
    session: AsyncSession,
):
    """Отозвать доступ у конкретного юзера."""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return
    
    user_id = int(callback.data.split(':')[2])
    user = await session.get(User, user_id)
    
    if not user:
        await callback.answer("Пользователь не найден", show_alert=True)
        return
    
    # Деактивируем все подписки
    stmt = select(Subscription).where(
        Subscription.user_id == user.id,
        Subscription.is_active == True,
    )
    result = await session.execute(stmt)
    subscriptions = result.scalars().all()
    
    count = 0
    for sub in subscriptions:
        sub.is_active = False
        count += 1
    
    await session.commit()
    
    # Логируем
    await log_admin_action(
        session=session,
        admin_telegram_id=callback.from_user.id,
        action="revoke_access",
        target_user_id=user.id,
        details={"subscriptions_revoked": count},
    )
    
    await callback.message.edit_text(
        f"✅ <b>Доступ отозван!</b>\n\n"
        f"Пользователь: {user.first_name} (@{user.username})\n"
        f"Деактивировано подписок: {count}",
        reply_markup=back_to_admin_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "admin:ban")
async def admin_ban_start(callback: CallbackQuery, state: FSMContext):
    """Начать бан юзера."""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return
    
    await state.set_state(AdminStates.ban_user_id)
    
    await callback.message.edit_text(
        "🚫 <b>Бан пользователя</b>\n\n"
        "Введите Telegram ID или @username:",
        reply_markup=back_to_admin_keyboard()
    )
    await callback.answer()


@router.message(AdminStates.ban_user_id)
async def admin_ban_user(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
):
    """Ввод юзера для бана."""
    query = message.text.strip()
    
    if query.startswith('@'):
        stmt = select(User).where(User.username == query[1:])
    elif query.isdigit():
        stmt = select(User).where(User.telegram_id == int(query))
    else:
        stmt = select(User).where(User.username == query)
    
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        await message.answer("❌ Пользователь не найден.", reply_markup=back_to_admin_keyboard())
        await state.clear()
        return
    
    await state.update_data(target_user_id=user.id)
    await state.set_state(AdminStates.ban_reason)
    
    await message.answer(
        f"👤 Пользователь: {user.first_name} (@{user.username})\n\n"
        "Введите причину бана (или '-' чтобы пропустить):",
        reply_markup=back_to_admin_keyboard()
    )


@router.message(AdminStates.ban_reason)
async def admin_ban_execute(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
):
    """Выполнить бан."""
    data = await state.get_data()
    target_user_id = data.get('target_user_id')
    
    user = await session.get(User, target_user_id)
    if not user:
        await message.answer("❌ Ошибка.", reply_markup=back_to_admin_keyboard())
        await state.clear()
        return
    
    reason = message.text.strip()
    if reason == '-':
        reason = None
    
    user.is_banned = True
    user.ban_reason = reason
    
    # Деактивируем подписки
    stmt = select(Subscription).where(
        Subscription.user_id == user.id,
        Subscription.is_active == True,
    )
    result = await session.execute(stmt)
    for sub in result.scalars().all():
        sub.is_active = False
    
    await session.commit()
    
    await log_admin_action(
        session=session,
        admin_telegram_id=message.from_user.id,
        action="ban_user",
        target_user_id=user.id,
        details={"reason": reason},
    )
    
    await message.answer(
        f"🚫 <b>Пользователь забанен!</b>\n\n"
        f"Пользователь: {user.first_name} (@{user.username})\n"
        f"Причина: {reason or 'Не указана'}",
        reply_markup=back_to_admin_keyboard()
    )
    await state.clear()


@router.callback_query(F.data.startswith("admin:ban_user:"))
async def admin_ban_user_direct(
    callback: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
):
    """Забанить конкретного юзера."""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return
    
    user_id = int(callback.data.split(':')[2])
    await state.update_data(target_user_id=user_id)
    await state.set_state(AdminStates.ban_reason)
    
    user = await session.get(User, user_id)
    
    await callback.message.edit_text(
        f"🚫 <b>Бан пользователя</b>\n\n"
        f"👤 {user.first_name} (@{user.username})\n\n"
        "Введите причину бана (или '-' чтобы пропустить):",
        reply_markup=back_to_admin_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "admin:unban")
async def admin_unban_start(callback: CallbackQuery, state: FSMContext):
    """Начать разбан."""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return
    
    await state.set_state(AdminStates.unban_user_id)
    
    await callback.message.edit_text(
        "✅ <b>Разбан пользователя</b>\n\n"
        "Введите Telegram ID или @username:",
        reply_markup=back_to_admin_keyboard()
    )
    await callback.answer()


@router.message(AdminStates.unban_user_id)
async def admin_unban_execute(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
):
    """Выполнить разбан."""
    query = message.text.strip()
    
    if query.startswith('@'):
        stmt = select(User).where(User.username == query[1:])
    elif query.isdigit():
        stmt = select(User).where(User.telegram_id == int(query))
    else:
        stmt = select(User).where(User.username == query)
    
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        await message.answer("❌ Пользователь не найден.", reply_markup=back_to_admin_keyboard())
        await state.clear()
        return
    
    user.is_banned = False
    user.ban_reason = None
    await session.commit()
    
    await log_admin_action(
        session=session,
        admin_telegram_id=message.from_user.id,
        action="unban_user",
        target_user_id=user.id,
    )
    
    await message.answer(
        f"✅ <b>Пользователь разбанен!</b>\n\n"
        f"Пользователь: {user.first_name} (@{user.username})",
        reply_markup=back_to_admin_keyboard()
    )
    await state.clear()


@router.callback_query(F.data.startswith("admin:unban_user:"))
async def admin_unban_user_direct(
    callback: CallbackQuery,
    session: AsyncSession,
):
    """Разбанить конкретного юзера."""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return
    
    user_id = int(callback.data.split(':')[2])
    user = await session.get(User, user_id)
    
    if not user:
        await callback.answer("Пользователь не найден", show_alert=True)
        return
    
    user.is_banned = False
    user.ban_reason = None
    await session.commit()
    
    await log_admin_action(
        session=session,
        admin_telegram_id=callback.from_user.id,
        action="unban_user",
        target_user_id=user.id,
    )
    
    await callback.message.edit_text(
        f"✅ <b>Пользователь разбанен!</b>\n\n"
        f"Пользователь: {user.first_name} (@{user.username})",
        reply_markup=back_to_admin_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "admin:manual_payment")
async def admin_manual_payment_start(callback: CallbackQuery, state: FSMContext):
    """Начать ручное подтверждение оплаты."""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return
    
    await state.set_state(AdminStates.manual_payment_user_id)
    
    await callback.message.edit_text(
        "💳 <b>Ручное подтверждение оплаты</b>\n\n"
        "Введите Telegram ID или @username пользователя:",
        reply_markup=back_to_admin_keyboard()
    )
    await callback.answer()


@router.message(AdminStates.manual_payment_user_id)
async def admin_manual_payment_user(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
):
    """Ввод юзера для ручной оплаты."""
    query = message.text.strip()
    
    if query.startswith('@'):
        stmt = select(User).where(User.username == query[1:])
    elif query.isdigit():
        stmt = select(User).where(User.telegram_id == int(query))
    else:
        stmt = select(User).where(User.username == query)
    
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        await message.answer("❌ Пользователь не найден.", reply_markup=back_to_admin_keyboard())
        await state.clear()
        return
    
    await state.update_data(target_user_id=user.id)
    await state.set_state(AdminStates.manual_payment_tariff)
    
    stmt = select(Tariff).where(Tariff.is_active == True).order_by(Tariff.sort_order)
    result = await session.execute(stmt)
    tariffs = result.scalars().all()
    
    buttons = []
    for tariff in tariffs:
        buttons.append([InlineKeyboardButton(
            text=f"{tariff.name_ru} ({tariff.price} USDT)",
            callback_data=f"admin:manual_tariff:{tariff.id}"
        )])
    buttons.append([InlineKeyboardButton(text="◀️ Отмена", callback_data="admin:menu")])
    
    await message.answer(
        f"👤 Пользователь: {user.first_name} (@{user.username})\n\n"
        "Выберите тариф для подтверждения оплаты:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )


@router.callback_query(F.data.startswith("admin:manual_tariff:"))
async def admin_manual_payment_execute(
    callback: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    bot: Bot,
):
    """Выполнить ручное подтверждение оплаты."""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return
    
    tariff_id = int(callback.data.split(':')[2])
    data = await state.get_data()
    target_user_id = data.get('target_user_id')
    
    user = await session.get(User, target_user_id)
    tariff = await session.get(Tariff, tariff_id, options=[
        selectinload(Tariff.tariff_channels).selectinload(TariffChannel.channel)
    ])
    
    if not user or not tariff:
        await callback.answer("Ошибка", show_alert=True)
        await state.clear()
        return
    
    # Создаём платёж
    payment = Payment(
        user_id=user.id,
        tariff_id=tariff.id,
        invoice_id=f"manual_{datetime.utcnow().timestamp()}",
        amount=tariff.price,
        original_amount=tariff.price,
        status="manual",
        payment_method="manual",
        confirmed_by=callback.from_user.id,
        paid_at=datetime.utcnow(),
    )
    session.add(payment)
    await session.flush()
    
    # Создаём подписку
    subscription = await create_subscription(
        session=session,
        user=user,
        tariff=tariff,
        payment=payment,
        granted_by=callback.from_user.id,
    )
    
    await log_admin_action(
        session=session,
        admin_telegram_id=callback.from_user.id,
        action="manual_payment",
        target_user_id=user.id,
        details={
            "tariff_id": tariff.id,
            "payment_id": payment.id,
            "amount": tariff.price,
        },
    )
    
    # Уведомляем юзера
    try:
        channels = await get_tariff_channels(session, tariff)
        
        if subscription.expires_at:
            expires = subscription.expires_at.strftime('%d.%m.%Y')
            user_text = (
                f"✅ <b>Оплата подтверждена!</b>\n\n"
                f"📦 Тариф: {tariff.name_ru}\n"
                f"⏱ Активен до: {expires}\n\n"
                f"🔗 Ссылки на каналы:"
            )
        else:
            user_text = (
                f"✅ <b>Оплата подтверждена!</b>\n\n"
                f"📦 Тариф: {tariff.name_ru}\n"
                f"⏱ Срок: Навсегда\n\n"
                f"🔗 Ссылки на каналы:"
            )
        
        await bot.send_message(user.telegram_id, user_text)
        
        for channel in channels:
            if channel.invite_link:
                await bot.send_message(
                    user.telegram_id,
                    f"📺 {channel.title}: {channel.invite_link}"
                )
    except:
        pass
    
    await callback.message.edit_text(
        f"✅ <b>Оплата подтверждена!</b>\n\n"
        f"Пользователь: {user.first_name} (@{user.username})\n"
        f"Тариф: {tariff.name_ru}\n"
        f"Сумма: {tariff.price} USDT",
        reply_markup=back_to_admin_keyboard()
    )
    await state.clear()
    await callback.answer()



@router.callback_query(F.data == "admin:broadcast")
async def admin_broadcast_start(callback: CallbackQuery, state: FSMContext):
    """Начать быструю рассылку - выбор фильтра."""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return
    
    buttons = [
        [InlineKeyboardButton(text="👥 Всем пользователям", callback_data="admin:broadcast_filter:all")],
        [InlineKeyboardButton(text="✅ С активной подпиской", callback_data="admin:broadcast_filter:active")],
        [InlineKeyboardButton(text="❌ Без подписки", callback_data="admin:broadcast_filter:inactive")],
        [InlineKeyboardButton(text="🇷🇺 Только RU", callback_data="admin:broadcast_filter:lang_ru")],
        [InlineKeyboardButton(text="🇬🇧 Только EN", callback_data="admin:broadcast_filter:lang_en")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin:menu")],
    ]
    
    await callback.message.edit_text(
        "📨 <b>Быстрая рассылка</b>\n\n"
        "Выберите фильтр получателей:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:broadcast_filter:"))
async def admin_broadcast_filter_select(
    callback: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
):
    """Выбор фильтра рассылки."""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return
    
    filter_value = callback.data.split(":")[2]
    
    # Определяем filter_type и filter_language
    filter_type = "all"
    filter_language = "all"
    filter_name = "Всем"
    
    if filter_value == "active":
        filter_type = "active"
        filter_name = "С активной подпиской"
    elif filter_value == "inactive":
        filter_type = "inactive"
        filter_name = "Без подписки"
    elif filter_value == "lang_ru":
        filter_language = "ru"
        filter_name = "Только RU"
    elif filter_value == "lang_en":
        filter_language = "en"
        filter_name = "Только EN"
    
    # Считаем получателей
    from bot.services.broadcast import count_broadcast_recipients
    count = await count_broadcast_recipients(session, filter_type, filter_language)
    
    await state.update_data(
        broadcast_filter_type=filter_type,
        broadcast_filter_language=filter_language,
        broadcast_filter_name=filter_name,
        broadcast_recipients_count=count,
    )
    await state.set_state(AdminStates.broadcast_text)
    
    await callback.message.edit_text(
        f"📨 <b>Быстрая рассылка</b>\n\n"
        f"Фильтр: <b>{filter_name}</b>\n"
        f"Получателей: <b>{count}</b>\n\n"
        f"Введите текст сообщения:\n"
        f"<i>Поддерживается HTML-разметка</i>",
        reply_markup=back_to_admin_keyboard()
    )
    await callback.answer()


@router.message(AdminStates.broadcast_text)
async def admin_broadcast_confirm(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
):
    """Подтверждение рассылки."""
    text = message.text or message.caption or ""
    
    if not text:
        await message.answer("❌ Текст не может быть пустым.", reply_markup=back_to_admin_keyboard())
        return
    
    data = await state.get_data()
    await state.update_data(broadcast_text=text)
    
    filter_name = data.get('broadcast_filter_name', 'Всем')
    count = data.get('broadcast_recipients_count', 0)
    
    buttons = [
        [InlineKeyboardButton(text=f"✅ Отправить {count} юзерам", callback_data="admin:broadcast_send")],
        [InlineKeyboardButton(text="🔄 Изменить фильтр", callback_data="admin:broadcast")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="admin:menu")],
    ]
    
    await message.answer(
        f"📨 <b>Подтверждение рассылки</b>\n\n"
        f"Фильтр: <b>{filter_name}</b>\n"
        f"Получателей: <b>{count}</b>\n\n"
        f"Текст:\n{text}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )


@router.callback_query(F.data == "admin:broadcast_send")
async def admin_broadcast_execute(
    callback: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    bot: Bot,
):
    """Выполнить рассылку."""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return
    
    data = await state.get_data()
    text = data.get('broadcast_text')
    filter_type = data.get('broadcast_filter_type', 'all')
    filter_language = data.get('broadcast_filter_language', 'all')
    
    if not text:
        await callback.answer("Ошибка: текст не найден", show_alert=True)
        await state.clear()
        return
    
    await callback.message.edit_text("⏳ Отправка...")
    
    # Используем сервис рассылок
    from bot.services.broadcast import quick_broadcast
    
    result = await quick_broadcast(
        session=session,
        bot=bot,
        message_text=text,
        filter_type=filter_type,
        filter_language=filter_language,
    )
    
    await log_admin_action(
        session=session,
        admin_telegram_id=callback.from_user.id,
        action="broadcast",
        details={
            "sent": result["sent"],
            "failed": result["failed"],
            "total": result["total"],
            "filter_type": filter_type,
            "filter_language": filter_language,
            "text": text[:100],
        },
    )
    
    await callback.message.edit_text(
        f"✅ <b>Рассылка завершена!</b>\n\n"
        f"📨 Отправлено: {result['sent']}\n"
        f"❌ Ошибок: {result['failed']}\n"
        f"👥 Всего: {result['total']}",
        reply_markup=back_to_admin_keyboard()
    )
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "admin:close")
async def admin_close(callback: CallbackQuery, state: FSMContext):
    """Закрыть админку."""
    await state.clear()
    await callback.message.delete()
    await callback.answer()
