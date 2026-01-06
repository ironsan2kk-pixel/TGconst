"""
Обработчик выбора канала
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery

from ..database import get_channel_by_id, get_tariffs_by_channel
from ..keyboards.inline import get_tariffs_keyboard, get_back_to_channels_keyboard

router = Router(name="channels")


@router.callback_query(F.data.startswith("channel:"))
async def select_channel(callback: CallbackQuery):
    """Обработка выбора канала"""
    # Извлекаем ID канала
    channel_id = int(callback.data.split(":")[1])
    
    # Получаем информацию о канале
    channel = await get_channel_by_id(channel_id)
    
    if not channel:
        await callback.answer("❌ Канал не найден", show_alert=True)
        return
    
    # Получаем тарифы канала
    tariffs = await get_tariffs_by_channel(channel_id)
    
    if not tariffs:
        await callback.message.edit_text(
            f"📢 <b>{channel['title']}</b>\n\n"
            "😔 К сожалению, для этого канала пока нет доступных тарифов.",
            reply_markup=get_back_to_channels_keyboard()
        )
        return
    
    # Формируем описание канала
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
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "back_to_channels")
async def back_to_channels(callback: CallbackQuery):
    """Вернуться к списку каналов"""
    from ..keyboards.inline import get_channels_keyboard
    
    keyboard = await get_channels_keyboard()
    
    if not keyboard:
        await callback.message.edit_text(
            "😔 К сожалению, сейчас нет доступных каналов."
        )
        return
    
    await callback.message.edit_text(
        "📢 <b>Доступные каналы</b>\n\n"
        "Выберите канал для просмотра тарифов:",
        reply_markup=keyboard
    )
    await callback.answer()
