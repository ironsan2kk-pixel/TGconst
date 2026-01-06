"""
Обработчик выбора тарифа
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery

from ..database import (
    get_tariff_by_id, 
    get_channel_by_id,
    get_user_by_telegram_id,
    get_active_subscription
)
from ..keyboards.inline import (
    get_payment_keyboard, 
    get_tariffs_keyboard,
    get_back_to_channels_keyboard
)

router = Router(name="tariffs")


@router.callback_query(F.data.startswith("tariff:"))
async def select_tariff(callback: CallbackQuery):
    """Обработка выбора тарифа"""
    # Извлекаем ID тарифа
    tariff_id = int(callback.data.split(":")[1])
    
    # Получаем информацию о тарифе
    tariff = await get_tariff_by_id(tariff_id)
    
    if not tariff:
        await callback.answer("❌ Тариф не найден", show_alert=True)
        return
    
    # Получаем канал
    channel = await get_channel_by_id(tariff["channel_id"])
    
    if not channel:
        await callback.answer("❌ Канал не найден", show_alert=True)
        return
    
    # Проверяем, есть ли уже активная подписка
    user = await get_user_by_telegram_id(callback.from_user.id)
    
    has_subscription = False
    if user:
        sub = await get_active_subscription(user["id"], channel["id"])
        if sub:
            has_subscription = True
    
    # Форматируем срок
    days = tariff["duration_days"]
    if days == 1:
        duration_text = "1 день"
    elif days < 5:
        duration_text = f"{days} дня"
    elif days == 30:
        duration_text = "1 месяц"
    elif days == 90:
        duration_text = "3 месяца"
    elif days == 180:
        duration_text = "6 месяцев"
    elif days == 365:
        duration_text = "1 год"
    else:
        duration_text = f"{days} дней"
    
    # Формируем текст с информацией о тарифе
    text = (
        f"📢 <b>{channel['title']}</b>\n\n"
        f"📦 <b>Тариф:</b> {tariff['name']}\n"
        f"⏱ <b>Срок:</b> {duration_text}\n"
        f"💰 <b>Стоимость:</b> ${tariff['price']:.2f}\n"
    )
    
    if has_subscription:
        text += (
            "\n⚠️ <i>У вас уже есть активная подписка на этот канал. "
            "Новая подписка продлит доступ.</i>\n"
        )
    
    text += "\n🎁 Есть промокод? Примените его при оплате!"
    
    # Клавиатура с кнопкой оплаты
    keyboard = get_payment_keyboard(tariff_id, tariff["channel_id"])
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("back_to_tariffs:"))
async def back_to_tariffs(callback: CallbackQuery):
    """Вернуться к списку тарифов канала"""
    from ..database import get_tariffs_by_channel
    
    channel_id = int(callback.data.split(":")[1])
    channel = await get_channel_by_id(channel_id)
    
    if not channel:
        await callback.answer("❌ Канал не найден", show_alert=True)
        return
    
    tariffs = await get_tariffs_by_channel(channel_id)
    
    if not tariffs:
        await callback.message.edit_text(
            f"📢 <b>{channel['title']}</b>\n\n"
            "😔 К сожалению, для этого канала пока нет доступных тарифов.",
            reply_markup=get_back_to_channels_keyboard(),
            parse_mode="HTML"
        )
        return
    
    channel_username = channel.get("channel_username")
    if channel_username:
        channel_link = f"@{channel_username}"
    else:
        channel_link = "Приватный канал"
    
    text = (
        f"📢 <b>{channel['title']}</b>\n"
        f"🔗 {channel_link}\n\n"
        "Выберите тариф:"
    )
    
    keyboard = get_tariffs_keyboard(tariffs, channel_id)
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


# Обработчики pay: и promo: перенесены в handlers/payment.py (Этап 9, 12)
