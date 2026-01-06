"""
Обработчик платежей через CryptoBot
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime
import logging
import sys
from pathlib import Path

from ..database import (
    get_tariff_by_id,
    get_channel_by_id,
    get_user_by_telegram_id,
    create_payment,
    validate_promocode,
    use_promocode,
    get_pending_payment
)
from ..keyboards.inline import get_confirm_payment_keyboard, get_back_to_channels_keyboard

logger = logging.getLogger(__name__)

router = Router(name="payment")


class PaymentStates(StatesGroup):
    """Состояния для процесса оплаты"""
    waiting_promocode = State()


def get_cryptobot_api(token: str):
    """Получить экземпляр CryptoBot API"""
    # Добавляем путь к backend/app для импорта
    project_root = Path(__file__).parent.parent.parent.parent
    sys.path.insert(0, str(project_root))
    from backend.app.services.cryptobot import CryptoBotAPI
    return CryptoBotAPI(token)


@router.callback_query(F.data.startswith("pay:"))
async def handle_payment_start(callback: CallbackQuery, state: FSMContext, bot_config: dict):
    """
    Начало процесса оплаты
    Формат callback: pay:{tariff_id}:{channel_id}
    """
    await callback.answer()
    
    parts = callback.data.split(":")
    tariff_id = int(parts[1])
    channel_id = int(parts[2]) if len(parts) > 2 else None
    
    # Получаем тариф
    tariff = await get_tariff_by_id(tariff_id)
    if not tariff:
        await callback.message.edit_text("❌ Тариф не найден или недоступен")
        return
    
    # Получаем канал
    channel = await get_channel_by_id(tariff["channel_id"])
    if not channel:
        await callback.message.edit_text("❌ Канал не найден")
        return
    
    # Получаем пользователя
    user = await get_user_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.message.edit_text("❌ Пользователь не найден. Нажмите /start")
        return
    
    # Получаем данные из state (промокод если был)
    data = await state.get_data()
    promocode = data.get("promocode")
    discount = data.get("discount", 0)
    
    # Вычисляем финальную цену
    original_price = tariff["price"]
    final_price = max(original_price - discount, 0)
    
    # Получаем токен CryptoBot из конфига бота
    cryptobot_token = bot_config.get("cryptobot_token")
    if not cryptobot_token:
        await callback.message.edit_text(
            "❌ Оплата временно недоступна.\n"
            "Обратитесь к администратору."
        )
        return
    
    try:
        # Создаём инвойс в CryptoBot
        api = get_cryptobot_api(cryptobot_token)
        
        # Формируем payload для идентификации платежа
        payload = f"{user['id']}:{tariff_id}"
        if promocode:
            payload += f":{promocode['id']}"
        
        invoice = await api.create_invoice(
            amount=final_price,
            asset="USDT",
            description=f"Подписка на {channel['title']} ({tariff['name']})",
            payload=payload,
            expires_in=3600  # 1 час
        )
        
        # Сохраняем платёж в БД
        payment_id = await create_payment(
            user_id=user["id"],
            tariff_id=tariff_id,
            amount=final_price,
            currency="USDT",
            invoice_id=str(invoice.invoice_id),
            promocode_id=promocode["id"] if promocode else None,
            discount_amount=discount
        )
        
        # Сохраняем в state
        await state.update_data(
            payment_id=payment_id,
            invoice_id=invoice.invoice_id,
            tariff_id=tariff_id,
            channel_id=channel["id"]
        )
        
    except Exception as e:
        logger.exception(f"Failed to create invoice: {e}")
        await callback.message.edit_text(
            "❌ Ошибка при создании счёта.\n"
            "Попробуйте позже или обратитесь в поддержку."
        )
        return
    
    # Показываем кнопку оплаты
    keyboard = get_confirm_payment_keyboard(
        invoice_url=invoice.pay_url,
        payment_id=payment_id
    )
    
    # Формируем текст
    text = (
        f"💳 <b>Счёт на оплату</b>\n\n"
        f"📺 Канал: <b>{channel['title']}</b>\n"
        f"📋 Тариф: <b>{tariff['name']}</b>\n"
        f"⏱ Срок: <b>{tariff['duration_days']} дн.</b>\n"
    )
    
    if discount > 0:
        text += f"\n💰 Цена: <s>${original_price:.2f}</s>\n"
        text += f"🎁 Скидка: -${discount:.2f}\n"
        text += f"✅ Итого: <b>${final_price:.2f} USDT</b>\n"
    else:
        text += f"💰 Сумма: <b>${final_price:.2f} USDT</b>\n"
    
    text += (
        f"\n⏱ Счёт действителен 1 час\n\n"
        f"Нажмите кнопку ниже для оплаты через @CryptoBot"
    )
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")


@router.callback_query(F.data.startswith("promo:"))
async def handle_enter_promo(callback: CallbackQuery, state: FSMContext):
    """
    Запрос ввода промокода
    Формат callback: promo:{tariff_id}:{channel_id}
    """
    await callback.answer()
    
    parts = callback.data.split(":")
    tariff_id = int(parts[1])
    channel_id = int(parts[2]) if len(parts) > 2 else None
    
    # Сохраняем контекст
    await state.update_data(tariff_id=tariff_id, channel_id=channel_id)
    await state.set_state(PaymentStates.waiting_promocode)
    
    await callback.message.edit_text(
        "🎁 <b>Введите промокод:</b>\n\n"
        "Отправьте код сообщением или нажмите /cancel для отмены",
        parse_mode="HTML"
    )


@router.message(PaymentStates.waiting_promocode)
async def handle_promocode_input(message: Message, state: FSMContext, bot_config: dict):
    """Обработка введённого промокода"""
    code = message.text.strip().upper()
    
    if code == "/CANCEL":
        await state.set_state(None)
        await message.answer("❌ Ввод промокода отменён")
        return
    
    data = await state.get_data()
    tariff_id = data.get("tariff_id")
    channel_id = data.get("channel_id")
    
    if not tariff_id:
        await state.set_state(None)
        await message.answer("❌ Ошибка. Попробуйте выбрать тариф заново.")
        return
    
    # Проверяем промокод
    is_valid, promocode, error_msg = await validate_promocode(code)
    
    if not is_valid:
        await message.answer(f"❌ {error_msg}")
        return
    
    # Получаем тариф для расчёта скидки
    tariff = await get_tariff_by_id(tariff_id)
    if not tariff:
        await state.set_state(None)
        await message.answer("❌ Тариф не найден")
        return
    
    # Вычисляем скидку
    original_price = tariff["price"]
    discount = 0.0
    
    if promocode.get("discount_percent"):
        discount = original_price * (promocode["discount_percent"] / 100)
    elif promocode.get("discount_amount"):
        discount = min(promocode["discount_amount"], original_price)
    
    final_price = max(original_price - discount, 0)
    
    # Сохраняем промокод в state
    await state.update_data(
        promocode=promocode,
        discount=discount,
        final_price=final_price
    )
    
    await state.set_state(None)
    
    # Получаем канал
    channel = await get_channel_by_id(tariff["channel_id"])
    
    # Формируем клавиатуру
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатить", callback_data=f"pay:{tariff_id}:{channel_id}")],
        [InlineKeyboardButton(text="🗑 Убрать промокод", callback_data=f"remove_promo:{tariff_id}:{channel_id}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data=f"channel:{channel_id}")]
    ])
    
    text = (
        f"📦 <b>Оформление подписки</b>\n\n"
        f"📺 Канал: <b>{channel['title']}</b>\n"
        f"📋 Тариф: <b>{tariff['name']}</b>\n"
        f"⏱ Срок: <b>{tariff['duration_days']} дн.</b>\n\n"
        f"💰 Цена: <s>${original_price:.2f}</s>\n"
        f"🎁 Промокод: <b>{code}</b> (-${discount:.2f})\n"
        f"✅ Итого: <b>${final_price:.2f}</b>"
    )
    
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")


@router.callback_query(F.data.startswith("remove_promo:"))
async def handle_remove_promo(callback: CallbackQuery, state: FSMContext):
    """Удаление промокода"""
    await callback.answer("Промокод удалён")
    
    parts = callback.data.split(":")
    tariff_id = int(parts[1])
    channel_id = int(parts[2]) if len(parts) > 2 else None
    
    # Очищаем данные промокода
    await state.update_data(
        promocode=None,
        discount=0,
        final_price=None
    )
    
    # Редиректим на выбор тарифа
    # Имитируем callback на tariff
    callback.data = f"tariff:{tariff_id}"
    from .tariffs import select_tariff
    await select_tariff(callback)


@router.callback_query(F.data.startswith("check_payment:"))
async def handle_check_payment(callback: CallbackQuery, state: FSMContext, bot_config: dict):
    """Проверка статуса оплаты"""
    payment_id = int(callback.data.split(":")[1])
    
    data = await state.get_data()
    invoice_id = data.get("invoice_id")
    
    if not invoice_id:
        await callback.answer("❌ Счёт не найден", show_alert=True)
        return
    
    cryptobot_token = bot_config.get("cryptobot_token")
    if not cryptobot_token:
        await callback.answer("❌ Ошибка конфигурации", show_alert=True)
        return
    
    try:
        api = get_cryptobot_api(cryptobot_token)
        invoice = await api.get_invoice(invoice_id)
        
        if not invoice:
            await callback.answer("❌ Инвойс не найден", show_alert=True)
            return
        
        if invoice.status == "paid":
            await callback.answer("✅ Оплата прошла!", show_alert=True)
            
            # Очищаем state
            tariff_id = data.get("tariff_id")
            channel_id = data.get("channel_id")
            await state.clear()
            
            # Получаем данные для сообщения
            tariff = await get_tariff_by_id(tariff_id)
            channel = await get_channel_by_id(channel_id) if channel_id else None
            
            keyboard = get_back_to_channels_keyboard()
            
            await callback.message.edit_text(
                f"✅ <b>Оплата прошла успешно!</b>\n\n"
                f"📺 Канал: <b>{channel['title'] if channel else 'Неизвестно'}</b>\n"
                f"📋 Тариф: <b>{tariff['name'] if tariff else 'Неизвестно'}</b>\n\n"
                f"Вы будете добавлены в канал в течение минуты.",
                reply_markup=keyboard,
                parse_mode="HTML"
            )
            
        elif invoice.status == "expired":
            await callback.answer("❌ Счёт истёк. Создайте новый.", show_alert=True)
        else:
            await callback.answer("⏳ Ожидаем оплату...", show_alert=True)
            
    except Exception as e:
        logger.exception(f"Error checking payment: {e}")
        await callback.answer("❌ Ошибка проверки. Попробуйте позже.", show_alert=True)


@router.callback_query(F.data == "cancel_payment")
async def handle_cancel_payment(callback: CallbackQuery, state: FSMContext):
    """Отмена платежа"""
    await callback.answer()
    await state.clear()
    
    keyboard = get_back_to_channels_keyboard()
    
    await callback.message.edit_text(
        "❌ Оплата отменена.\n\n"
        "Вы можете оформить подписку позже.",
        reply_markup=keyboard
    )
