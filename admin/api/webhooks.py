"""
Webhook endpoints для приёма уведомлений от CryptoBot.
"""

import json
from datetime import datetime

from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from admin.database import get_session
from bot.config import config
from bot.models import Payment, User, Tariff
from bot.services.cryptobot import CryptoBotAPI

router = APIRouter()


async def process_cryptobot_payment(
    invoice_id: str,
    payload_data: dict,
) -> None:
    """
    Фоновая обработка успешного платежа из CryptoBot webhook.
    
    Args:
        invoice_id: ID инвойса
        payload_data: Данные из payload
    """
    from bot.loader import bot
    from bot.services.subscription import create_subscription, get_tariff_channels
    from bot.services.notifications import notify_admins
    from bot.locales import get_text
    
    async for session in get_session():
        # Находим платёж
        stmt = select(Payment).where(Payment.invoice_id == invoice_id)
        result = await session.execute(stmt)
        payment = result.scalar_one_or_none()
        
        if not payment:
            print(f"Payment not found for invoice {invoice_id}")
            return
        
        # Уже обработан?
        if payment.status == "paid":
            print(f"Payment {payment.id} already processed")
            return
        
        # Получаем пользователя
        user = await session.get(User, payment.user_id)
        if not user:
            print(f"User not found for payment {payment.id}")
            return
        
        # Получаем тариф
        tariff = await session.get(Tariff, payment.tariff_id)
        if not tariff:
            print(f"Tariff not found for payment {payment.id}")
            return
        
        # Обновляем статус платежа
        payment.status = "paid"
        payment.paid_at = datetime.utcnow()
        
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
        
        lang = user.language or "ru"
        _ = lambda key: get_text(key, lang)
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
        
        # Отправляем сообщение пользователю
        try:
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text=_('menu.my_subscriptions'),
                    callback_data="my_subscriptions"
                )],
                [InlineKeyboardButton(
                    text=_('menu.back'),
                    callback_data="back_to_menu"
                )],
            ])
            
            await bot.send_message(user.telegram_id, text, reply_markup=keyboard)
            
            # Отправляем ссылки на каналы
            for channel in channels:
                if channel.invite_link:
                    channel_text = _('payment.channel_link').format(
                        title=channel.title,
                        link=channel.invite_link
                    )
                    await bot.send_message(user.telegram_id, channel_text)
            
            # Уведомляем админов
            admin_text = get_text('admin.new_payment', 'ru').format(
                name=user.first_name or "Unknown",
                username=user.username or "нет",
                user_id=user.telegram_id,
                tariff=tariff_name,
                amount=payment.amount,
            )
            await notify_admins(bot, admin_text)
            
        except Exception as e:
            print(f"Error sending payment notification: {e}")


@router.post("/cryptobot")
async def cryptobot_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
):
    """
    Webhook для приёма уведомлений от CryptoBot.
    
    CryptoBot отправляет POST запрос с данными об оплаченном инвойсе.
    """
    # Получаем тело запроса
    body = await request.body()
    
    # Проверяем подпись
    signature = request.headers.get("crypto-pay-api-signature", "")
    
    if signature:
        if not CryptoBotAPI.verify_webhook_signature(body, signature):
            raise HTTPException(status_code=403, detail="Invalid signature")
    
    # Парсим данные
    try:
        data = await request.json()
    except:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    # Проверяем тип обновления
    update_type = data.get("update_type")
    
    if update_type != "invoice_paid":
        # Игнорируем другие типы
        return {"ok": True}
    
    # Получаем данные инвойса
    invoice = data.get("payload", {})
    invoice_id = str(invoice.get("invoice_id", ""))
    status = invoice.get("status")
    
    if not invoice_id or status != "paid":
        return {"ok": True}
    
    # Получаем payload из инвойса
    payload_str = invoice.get("payload", "{}")
    try:
        payload_data = json.loads(payload_str) if payload_str else {}
    except:
        payload_data = {}
    
    # Запускаем обработку в фоне
    background_tasks.add_task(
        process_cryptobot_payment,
        invoice_id=invoice_id,
        payload_data=payload_data,
    )
    
    return {"ok": True}


@router.get("/cryptobot/test")
async def test_webhook():
    """Тестовый endpoint для проверки доступности webhook."""
    return {
        "status": "ok",
        "message": "CryptoBot webhook is ready",
        "cryptobot_configured": bool(config.CRYPTOBOT_TOKEN),
    }
