"""
Обработчик платежей через CryptoBot
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select
from datetime import datetime
import logging

from ..database import get_session
from ..loader import bot, config
from ..models import User, Tariff, Channel, Payment, Promocode

logger = logging.getLogger(__name__)

router = Router()


class PaymentStates(StatesGroup):
    """Состояния для процесса оплаты"""
    waiting_promocode = State()


async def get_cryptobot_api():
    """Получить экземпляр CryptoBot API"""
    import sys
    sys.path.insert(0, str(config.base_path.parent.parent))
    from app.services.cryptobot import CryptoBotAPI
    return CryptoBotAPI(config.cryptobot_token)


async def calculate_price(tariff: Tariff, promocode: Promocode = None) -> tuple[float, float]:
    """
    Рассчитать цену с учётом промокода
    
    Returns:
        tuple: (финальная цена, размер скидки)
    """
    original_price = tariff.price
    discount = 0.0
    
    if promocode:
        if promocode.discount_percent:
            discount = original_price * (promocode.discount_percent / 100)
        elif promocode.discount_amount:
            discount = min(promocode.discount_amount, original_price)
    
    final_price = max(original_price - discount, 0)
    return final_price, discount


@router.callback_query(F.data.startswith("pay:"))
async def handle_payment_start(callback: CallbackQuery, state: FSMContext):
    """
    Начало процесса оплаты
    Формат callback: pay:{tariff_id}
    """
    await callback.answer()
    
    tariff_id = int(callback.data.split(":")[1])
    
    async with get_session() as session:
        # Получаем тариф
        stmt = select(Tariff).where(Tariff.id == tariff_id, Tariff.is_active == True)
        result = await session.execute(stmt)
        tariff = result.scalar_one_or_none()
        
        if not tariff:
            await callback.message.edit_text("❌ Тариф не найден или недоступен")
            return
        
        # Получаем канал
        stmt = select(Channel).where(Channel.id == tariff.channel_id)
        result = await session.execute(stmt)
        channel = result.scalar_one_or_none()
        
        if not channel:
            await callback.message.edit_text("❌ Канал не найден")
            return
        
        # Получаем пользователя
        stmt = select(User).where(User.telegram_id == callback.from_user.id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            await callback.message.edit_text("❌ Пользователь не найден")
            return
        
        # Сохраняем в state
        await state.update_data(
            tariff_id=tariff.id,
            channel_id=channel.id,
            user_id=user.id,
            original_price=tariff.price,
            tariff_name=tariff.name,
            channel_title=channel.title,
            duration_days=tariff.duration_days
        )
    
    # Показываем информацию и опцию промокода
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎟 Ввести промокод", callback_data="enter_promo")],
        [InlineKeyboardButton(text="💳 Оплатить", callback_data="create_invoice")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data=f"channel:{tariff.channel_id}")]
    ])
    
    text = (
        f"📦 <b>Оформление подписки</b>\n\n"
        f"📺 Канал: <b>{channel.title}</b>\n"
        f"📋 Тариф: <b>{tariff.name}</b>\n"
        f"⏱ Срок: <b>{tariff.duration_days} дн.</b>\n"
        f"💰 Стоимость: <b>${tariff.price:.2f}</b>\n\n"
        f"Выберите действие:"
    )
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")


@router.callback_query(F.data == "enter_promo")
async def handle_enter_promo(callback: CallbackQuery, state: FSMContext):
    """Запрос ввода промокода"""
    await callback.answer()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_promo")]
    ])
    
    await callback.message.edit_text(
        "🎟 <b>Введите промокод:</b>\n\n"
        "Отправьте код сообщением",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    
    await state.set_state(PaymentStates.waiting_promocode)


@router.message(PaymentStates.waiting_promocode)
async def handle_promocode_input(message: Message, state: FSMContext):
    """Обработка введённого промокода"""
    code = message.text.strip().upper()
    data = await state.get_data()
    
    async with get_session() as session:
        # Ищем промокод
        stmt = select(Promocode).where(
            Promocode.code == code,
            Promocode.is_active == True
        )
        result = await session.execute(stmt)
        promocode = result.scalar_one_or_none()
        
        if not promocode:
            await message.answer("❌ Промокод не найден или недействителен")
            return
        
        # Проверяем срок действия
        now = datetime.utcnow()
        if promocode.valid_from and now < promocode.valid_from:
            await message.answer("❌ Промокод ещё не активен")
            return
        
        if promocode.valid_until and now > promocode.valid_until:
            await message.answer("❌ Промокод истёк")
            return
        
        # Проверяем лимит использований
        if promocode.max_uses and promocode.used_count >= promocode.max_uses:
            await message.answer("❌ Промокод исчерпан")
            return
        
        # Получаем тариф для расчёта скидки
        stmt = select(Tariff).where(Tariff.id == data['tariff_id'])
        result = await session.execute(stmt)
        tariff = result.scalar_one_or_none()
        
        if not tariff:
            await message.answer("❌ Ошибка: тариф не найден")
            return
        
        final_price, discount = await calculate_price(tariff, promocode)
        
        # Сохраняем промокод в state
        await state.update_data(
            promocode_id=promocode.id,
            promocode_code=promocode.code,
            discount=discount,
            final_price=final_price
        )
        
        await state.set_state(None)
    
    # Показываем обновлённую цену
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатить", callback_data="create_invoice")],
        [InlineKeyboardButton(text="🗑 Убрать промокод", callback_data="remove_promo")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data=f"channel:{data['channel_id']}")]
    ])
    
    text = (
        f"📦 <b>Оформление подписки</b>\n\n"
        f"📺 Канал: <b>{data['channel_title']}</b>\n"
        f"📋 Тариф: <b>{data['tariff_name']}</b>\n"
        f"⏱ Срок: <b>{data['duration_days']} дн.</b>\n\n"
        f"💰 Цена: <s>${data['original_price']:.2f}</s>\n"
        f"🎟 Промокод: <b>{code}</b> (-${discount:.2f})\n"
        f"✅ Итого: <b>${final_price:.2f}</b>"
    )
    
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")


@router.callback_query(F.data == "cancel_promo")
async def handle_cancel_promo(callback: CallbackQuery, state: FSMContext):
    """Отмена ввода промокода"""
    await callback.answer()
    await state.set_state(None)
    
    data = await state.get_data()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎟 Ввести промокод", callback_data="enter_promo")],
        [InlineKeyboardButton(text="💳 Оплатить", callback_data="create_invoice")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data=f"channel:{data['channel_id']}")]
    ])
    
    text = (
        f"📦 <b>Оформление подписки</b>\n\n"
        f"📺 Канал: <b>{data['channel_title']}</b>\n"
        f"📋 Тариф: <b>{data['tariff_name']}</b>\n"
        f"⏱ Срок: <b>{data['duration_days']} дн.</b>\n"
        f"💰 Стоимость: <b>${data['original_price']:.2f}</b>"
    )
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")


@router.callback_query(F.data == "remove_promo")
async def handle_remove_promo(callback: CallbackQuery, state: FSMContext):
    """Удаление промокода"""
    await callback.answer("Промокод удалён")
    
    # Очищаем данные промокода
    await state.update_data(
        promocode_id=None,
        promocode_code=None,
        discount=0,
        final_price=None
    )
    
    data = await state.get_data()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎟 Ввести промокод", callback_data="enter_promo")],
        [InlineKeyboardButton(text="💳 Оплатить", callback_data="create_invoice")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data=f"channel:{data['channel_id']}")]
    ])
    
    text = (
        f"📦 <b>Оформление подписки</b>\n\n"
        f"📺 Канал: <b>{data['channel_title']}</b>\n"
        f"📋 Тариф: <b>{data['tariff_name']}</b>\n"
        f"⏱ Срок: <b>{data['duration_days']} дн.</b>\n"
        f"💰 Стоимость: <b>${data['original_price']:.2f}</b>"
    )
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")


@router.callback_query(F.data == "create_invoice")
async def handle_create_invoice(callback: CallbackQuery, state: FSMContext):
    """Создание инвойса CryptoBot"""
    await callback.answer("⏳ Создаём счёт...")
    
    data = await state.get_data()
    
    # Определяем финальную цену
    final_price = data.get('final_price') or data['original_price']
    
    if final_price <= 0:
        # Если бесплатно (100% скидка) - сразу активируем
        await activate_free_subscription(callback, state, data)
        return
    
    async with get_session() as session:
        # Получаем пользователя
        stmt = select(User).where(User.id == data['user_id'])
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            await callback.message.edit_text("❌ Ошибка: пользователь не найден")
            return
        
        try:
            # Создаём инвойс в CryptoBot
            api = await get_cryptobot_api()
            
            # Формируем payload для идентификации платежа
            payload = f"{user.id}:{data['tariff_id']}"
            if data.get('promocode_id'):
                payload += f":{data['promocode_id']}"
            
            invoice = await api.create_invoice(
                amount=final_price,
                asset="USDT",
                description=f"Подписка на {data['channel_title']} ({data['tariff_name']})",
                payload=payload,
                paid_btn_name="callback",
                paid_btn_url=f"https://t.me/{(await bot.get_me()).username}?start=paid_{data['tariff_id']}",
                expires_in=3600  # 1 час
            )
            
            # Сохраняем платёж в БД
            payment = Payment(
                user_id=user.id,
                invoice_id=str(invoice.invoice_id),
                amount=final_price,
                currency="USDT",
                status="pending",
                promocode_id=data.get('promocode_id'),
                discount_amount=data.get('discount', 0),
                created_at=datetime.utcnow()
            )
            session.add(payment)
            await session.commit()
            
            # Сохраняем ID платежа
            await state.update_data(payment_id=payment.id, invoice_id=invoice.invoice_id)
            
        except Exception as e:
            logger.exception(f"Failed to create invoice: {e}")
            await callback.message.edit_text(
                "❌ Ошибка при создании счёта. Попробуйте позже."
            )
            return
    
    # Показываем кнопку оплаты
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатить в CryptoBot", url=invoice.pay_url)],
        [InlineKeyboardButton(text="🔄 Проверить оплату", callback_data=f"check_payment:{invoice.invoice_id}")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_payment")]
    ])
    
    text = (
        f"💳 <b>Счёт на оплату</b>\n\n"
        f"📺 Канал: <b>{data['channel_title']}</b>\n"
        f"📋 Тариф: <b>{data['tariff_name']}</b>\n"
        f"💰 Сумма: <b>${final_price:.2f} USDT</b>\n\n"
        f"⏱ Счёт действителен 1 час\n\n"
        f"Нажмите кнопку ниже для оплаты через @CryptoBot"
    )
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")


async def activate_free_subscription(callback: CallbackQuery, state: FSMContext, data: dict):
    """Активация бесплатной подписки (100% скидка)"""
    from datetime import timedelta
    
    async with get_session() as session:
        # Создаём подписку
        from ..models import Subscription
        
        starts_at = datetime.utcnow()
        expires_at = starts_at + timedelta(days=data['duration_days'])
        
        subscription = Subscription(
            user_id=data['user_id'],
            channel_id=data['channel_id'],
            tariff_id=data['tariff_id'],
            starts_at=starts_at,
            expires_at=expires_at,
            is_active=True,
            auto_kicked=False
        )
        session.add(subscription)
        
        # Создаём запись о платеже
        payment = Payment(
            user_id=data['user_id'],
            invoice_id=f"FREE_{datetime.utcnow().timestamp()}",
            amount=0,
            currency="USDT",
            status="paid",
            promocode_id=data.get('promocode_id'),
            discount_amount=data['original_price'],
            paid_at=datetime.utcnow(),
            created_at=datetime.utcnow()
        )
        session.add(payment)
        
        # Увеличиваем счётчик промокода
        if data.get('promocode_id'):
            stmt = select(Promocode).where(Promocode.id == data['promocode_id'])
            result = await session.execute(stmt)
            promocode = result.scalar_one_or_none()
            if promocode:
                promocode.used_count += 1
        
        await session.commit()
    
    await state.clear()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Мои подписки", callback_data="my_subscriptions")],
        [InlineKeyboardButton(text="🏠 В меню", callback_data="main_menu")]
    ])
    
    await callback.message.edit_text(
        f"✅ <b>Подписка активирована!</b>\n\n"
        f"📺 Канал: <b>{data['channel_title']}</b>\n"
        f"📋 Тариф: <b>{data['tariff_name']}</b>\n"
        f"🎟 Промокод: 100% скидка\n\n"
        f"Вы будете добавлены в канал в течение минуты.",
        reply_markup=keyboard,
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("check_payment:"))
async def handle_check_payment(callback: CallbackQuery, state: FSMContext):
    """Проверка статуса оплаты"""
    invoice_id = int(callback.data.split(":")[1])
    
    try:
        api = await get_cryptobot_api()
        invoice = await api.get_invoice(invoice_id)
        
        if not invoice:
            await callback.answer("❌ Инвойс не найден", show_alert=True)
            return
        
        if invoice.status == "paid":
            # Оплата прошла - обновляем статус
            data = await state.get_data()
            
            async with get_session() as session:
                # Обновляем платёж
                stmt = select(Payment).where(Payment.invoice_id == str(invoice_id))
                result = await session.execute(stmt)
                payment = result.scalar_one_or_none()
                
                if payment and payment.status != "paid":
                    from datetime import timedelta
                    from ..models import Subscription
                    
                    payment.status = "paid"
                    payment.paid_at = invoice.paid_at or datetime.utcnow()
                    
                    # Создаём подписку
                    starts_at = datetime.utcnow()
                    expires_at = starts_at + timedelta(days=data['duration_days'])
                    
                    subscription = Subscription(
                        user_id=data['user_id'],
                        channel_id=data['channel_id'],
                        tariff_id=data['tariff_id'],
                        starts_at=starts_at,
                        expires_at=expires_at,
                        is_active=True,
                        auto_kicked=False
                    )
                    session.add(subscription)
                    
                    await session.flush()
                    payment.subscription_id = subscription.id
                    
                    # Увеличиваем счётчик промокода
                    if data.get('promocode_id'):
                        stmt = select(Promocode).where(Promocode.id == data['promocode_id'])
                        result = await session.execute(stmt)
                        promocode = result.scalar_one_or_none()
                        if promocode:
                            promocode.used_count += 1
                    
                    await session.commit()
            
            await state.clear()
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📋 Мои подписки", callback_data="my_subscriptions")],
                [InlineKeyboardButton(text="🏠 В меню", callback_data="main_menu")]
            ])
            
            await callback.message.edit_text(
                f"✅ <b>Оплата прошла успешно!</b>\n\n"
                f"📺 Канал: <b>{data['channel_title']}</b>\n"
                f"📋 Тариф: <b>{data['tariff_name']}</b>\n\n"
                f"Вы будете добавлены в канал в течение минуты.",
                reply_markup=keyboard,
                parse_mode="HTML"
            )
            
        elif invoice.status == "expired":
            await callback.answer("❌ Счёт истёк. Создайте новый.", show_alert=True)
            
            # Обновляем статус в БД
            async with get_session() as session:
                stmt = select(Payment).where(Payment.invoice_id == str(invoice_id))
                result = await session.execute(stmt)
                payment = result.scalar_one_or_none()
                if payment:
                    payment.status = "expired"
                    await session.commit()
        else:
            await callback.answer("⏳ Ожидаем оплату...", show_alert=True)
            
    except Exception as e:
        logger.exception(f"Error checking payment: {e}")
        await callback.answer("❌ Ошибка проверки. Попробуйте позже.", show_alert=True)


@router.callback_query(F.data == "cancel_payment")
async def handle_cancel_payment(callback: CallbackQuery, state: FSMContext):
    """Отмена платежа"""
    await callback.answer()
    
    data = await state.get_data()
    
    # Обновляем статус платежа
    if data.get('invoice_id'):
        async with get_session() as session:
            stmt = select(Payment).where(Payment.invoice_id == str(data['invoice_id']))
            result = await session.execute(stmt)
            payment = result.scalar_one_or_none()
            if payment and payment.status == "pending":
                payment.status = "cancelled"
                await session.commit()
    
    await state.clear()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📺 К каналам", callback_data="channels")],
        [InlineKeyboardButton(text="🏠 В меню", callback_data="main_menu")]
    ])
    
    await callback.message.edit_text(
        "❌ Оплата отменена.\n\n"
        "Вы можете оформить подписку позже.",
        reply_markup=keyboard
    )
