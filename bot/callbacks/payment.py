"""
Callback-обработчики процесса оплаты через CryptoBot.
"""

import json
from datetime import datetime

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bot.config import config
from bot.models import User, Tariff, TariffChannel, Payment
from bot.keyboards import back_to_menu_keyboard, main_menu_keyboard
from bot.locales import get_text
from bot.services.cryptobot import cryptobot, CryptoBotError
from bot.services.subscription import create_subscription, get_tariff_channels
from bot.services.notifications import notify_admins

router = Router()


def payment_keyboard(
    pay_url: str,
    amount: float,
    payment_id: int,
    lang: str,
) -> InlineKeyboardMarkup:
    """Клавиатура для оплаты."""
    _ = lambda key: get_text(key, lang)
    
    buttons = [
        [InlineKeyboardButton(
            text=_('payment.pay_button').format(amount=amount),
            url=pay_url
        )],
        [InlineKeyboardButton(
            text=_('payment.check_payment'),
            callback_data=f"check_payment:{payment_id}"
        )],
        [InlineKeyboardButton(
            text=_('payment.cancel'),
            callback_data=f"cancel_payment:{payment_id}"
        )],
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def success_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Клавиатура после успешной оплаты."""
    _ = lambda key: get_text(key, lang)
    
    buttons = [
        [InlineKeyboardButton(
            text=_('menu.my_subscriptions'),
            callback_data="my_subscriptions"
        )],
        [InlineKeyboardButton(
            text=_('menu.back'),
            callback_data="back_to_menu"
        )],
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.callback_query(F.data.startswith("pay:"))
async def start_payment(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    lang: str,
    _: callable,
    bot: Bot,
):
    """Начать процесс оплаты."""
    tariff_id = int(callback.data.split(':')[1])
    
    # Получаем тариф
    tariff = await session.get(Tariff, tariff_id)
    
    if not tariff or not tariff.is_active:
        await callback.answer(_('error'), show_alert=True)
        return
    
    # Проверяем настроен ли CryptoBot
    if not cryptobot.is_configured:
        await callback.message.edit_text(
            _('payment.cryptobot_disabled'),
            reply_markup=back_to_menu_keyboard(lang)
        )
        await callback.answer()
        return
    
    # Показываем сообщение о создании счёта
    await callback.message.edit_text(_('payment.creating'))
    
    try:
        # Создаём инвойс в CryptoBot
        tariff_name = tariff.name_ru if lang == 'ru' else tariff.name_en
        
        # Payload для идентификации платежа
        payload = json.dumps({
            "user_id": user.id,
            "tariff_id": tariff.id,
            "telegram_id": user.telegram_id,
        })
        
        invoice = await cryptobot.create_invoice(
            amount=tariff.price,
            currency="USDT",
            description=f"Подписка: {tariff_name}",
            payload=payload,
            expires_in=3600,  # 1 час
        )
        
        # Создаём запись платежа в БД
        payment = Payment(
            user_id=user.id,
            tariff_id=tariff.id,
            invoice_id=str(invoice.get("invoice_id")),
            amount=tariff.price,
            original_amount=tariff.price,
            status="pending",
            payment_method="cryptobot",
        )
        
        session.add(payment)
        await session.commit()
        
        # Формируем сообщение
        pay_url = invoice.get("bot_invoice_url") or invoice.get("pay_url")
        
        text = _('payment.invoice_created').format(
            tariff=tariff_name,
            amount=tariff.price,
            discount=""
        )
        
        await callback.message.edit_text(
            text,
            reply_markup=payment_keyboard(pay_url, tariff.price, payment.id, lang)
        )
        
    except CryptoBotError as e:
        await callback.message.edit_text(
            f"❌ Ошибка создания счёта: {str(e)}",
            reply_markup=back_to_menu_keyboard(lang)
        )
    
    await callback.answer()


@router.callback_query(F.data.startswith("check_payment:"))
async def check_payment(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    lang: str,
    _: callable,
    bot: Bot,
):
    """Проверить статус оплаты."""
    payment_id = int(callback.data.split(':')[1])
    
    # Получаем платёж
    payment = await session.get(Payment, payment_id)
    
    if not payment or payment.user_id != user.id:
        await callback.answer(_('error'), show_alert=True)
        return
    
    # Уже оплачен?
    if payment.status == "paid":
        await callback.answer(_('payment.already_paid'), show_alert=True)
        return
    
    # Отменён или истёк?
    if payment.status in ("cancelled", "expired"):
        await callback.answer(_('payment.expired'), show_alert=True)
        return
    
    try:
        # Проверяем статус в CryptoBot
        invoice = await cryptobot.get_invoice(payment.invoice_id)
        
        if not invoice:
            payment.status = "expired"
            await session.commit()
            await callback.message.edit_text(
                _('payment.expired'),
                reply_markup=back_to_menu_keyboard(lang)
            )
            await callback.answer()
            return
        
        status = invoice.get("status")
        
        if status == "paid":
            # Оплачено! Создаём подписку
            await process_successful_payment(
                session=session,
                payment=payment,
                user=user,
                lang=lang,
                callback=callback,
                bot=bot,
                _=_,
            )
        elif status == "expired":
            payment.status = "expired"
            await session.commit()
            await callback.message.edit_text(
                _('payment.expired'),
                reply_markup=back_to_menu_keyboard(lang)
            )
            await callback.answer()
        else:
            # Ещё не оплачен
            await callback.answer(_('payment.pending'), show_alert=True)
            
    except CryptoBotError as e:
        await callback.answer(f"Ошибка: {str(e)}", show_alert=True)


@router.callback_query(F.data.startswith("cancel_payment:"))
async def cancel_payment(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    lang: str,
    _: callable,
):
    """Отменить платёж."""
    payment_id = int(callback.data.split(':')[1])
    
    # Получаем платёж
    payment = await session.get(Payment, payment_id)
    
    if not payment or payment.user_id != user.id:
        await callback.answer(_('error'), show_alert=True)
        return
    
    if payment.status == "pending":
        payment.status = "cancelled"
        await session.commit()
        
        # Пытаемся удалить инвойс в CryptoBot
        try:
            await cryptobot.delete_invoice(int(payment.invoice_id))
        except:
            pass
    
    await callback.message.edit_text(
        _('payment.cancelled'),
        reply_markup=back_to_menu_keyboard(lang)
    )
    await callback.answer()


async def process_successful_payment(
    session: AsyncSession,
    payment: Payment,
    user: User,
    lang: str,
    callback: CallbackQuery | None = None,
    message_chat_id: int | None = None,
    bot: Bot | None = None,
    _: callable | None = None,
) -> None:
    """
    Обработать успешный платёж.
    
    Вызывается либо из callback проверки, либо из webhook.
    
    Args:
        session: Сессия БД
        payment: Платёж
        user: Пользователь
        lang: Язык
        callback: Callback query (если из кнопки)
        message_chat_id: Chat ID для отправки сообщения (если из webhook)
        bot: Bot instance
        _: Функция перевода
    """
    if _ is None:
        _ = lambda key: get_text(key, lang)
    
    # Обновляем статус платежа
    payment.status = "paid"
    payment.paid_at = datetime.utcnow()
    
    # Получаем тариф с каналами
    stmt = select(Tariff).where(
        Tariff.id == payment.tariff_id
    ).options(
        selectinload(Tariff.tariff_channels).selectinload(TariffChannel.channel)
    )
    result = await session.execute(stmt)
    tariff = result.scalar_one_or_none()
    
    if not tariff:
        return
    
    # Создаём подписку
    subscription = await create_subscription(
        session=session,
        user=user,
        tariff=tariff,
        payment=payment,
        is_trial=False,
    )
    
    # Получаем каналы
    channels = await get_tariff_channels(session, tariff)
    
    tariff_name = tariff.name_ru if lang == 'ru' else tariff.name_en
    
    # Формируем текст успеха
    if subscription.expires_at:
        expires_str = subscription.expires_at.strftime("%d.%m.%Y %H:%M")
        text = _('payment.success').format(
            tariff=tariff_name,
            expires=expires_str
        )
    else:
        text = _('payment.success_forever').format(tariff=tariff_name)
    
    keyboard = success_keyboard(lang)
    
    # Отправляем сообщение
    if callback:
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
        chat_id = callback.message.chat.id
    elif message_chat_id and bot:
        await bot.send_message(message_chat_id, text, reply_markup=keyboard)
        chat_id = message_chat_id
    else:
        return
    
    # Отправляем ссылки на каналы
    if channels and bot:
        for channel in channels:
            if channel.invite_link:
                channel_text = _('payment.channel_link').format(
                    title=channel.title,
                    link=channel.invite_link
                )
                await bot.send_message(chat_id, channel_text)
    
    # Уведомляем админов
    if bot:
        admin_text = get_text('admin.new_payment', 'ru').format(
            name=user.first_name or "Unknown",
            username=user.username or "нет",
            user_id=user.telegram_id,
            tariff=tariff_name,
            amount=payment.amount,
        )
        await notify_admins(bot, admin_text)
