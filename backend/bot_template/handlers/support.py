"""
Обработчик поддержки
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import Dict, Any, Optional
import logging

from ..database import get_user_by_telegram_id, get_user_subscriptions
from ..keyboards.reply import get_main_menu_keyboard

logger = logging.getLogger(__name__)

router = Router(name="support")


class SupportStates(StatesGroup):
    """Состояния для обращения в поддержку"""
    waiting_message = State()


# FAQ вопросы и ответы
FAQ_ITEMS = [
    {
        "id": "payment",
        "question": "💳 Как оплатить подписку?",
        "answer": (
            "Оплата производится через @CryptoBot в криптовалюте:\n\n"
            "1️⃣ Выберите канал в разделе «📢 Каналы»\n"
            "2️⃣ Выберите подходящий тариф\n"
            "3️⃣ Если есть промокод — введите его\n"
            "4️⃣ Нажмите «💳 Оплатить» и перейдите в CryptoBot\n"
            "5️⃣ Оплатите счёт любой криптовалютой\n"
            "6️⃣ Вернитесь и нажмите «🔄 Проверить оплату»\n\n"
            "После подтверждения оплаты вы будете автоматически добавлены в канал."
        )
    },
    {
        "id": "access",
        "question": "🔐 Когда я получу доступ?",
        "answer": (
            "После успешной оплаты вы получите доступ автоматически в течение 1-2 минут.\n\n"
            "Если доступ не появился:\n"
            "• Проверьте статус оплаты в @CryptoBot\n"
            "• Убедитесь, что ваш аккаунт не ограничен Telegram\n"
            "• Обратитесь в поддержку с номером транзакции"
        )
    },
    {
        "id": "extend",
        "question": "🔄 Как продлить подписку?",
        "answer": (
            "Для продления подписки:\n\n"
            "1️⃣ Перейдите в «📋 Мои подписки»\n"
            "2️⃣ Нажмите «🔄 Продлить» у нужной подписки\n"
            "3️⃣ Выберите тариф и оплатите\n\n"
            "💡 Новый срок добавится к текущему, даже если подписка ещё не истекла."
        )
    },
    {
        "id": "promo",
        "question": "🎁 Как использовать промокод?",
        "answer": (
            "Есть два способа:\n\n"
            "<b>Способ 1:</b> Перед покупкой\n"
            "• Нажмите «🎁 Промокод» в главном меню\n"
            "• Введите код\n"
            "• Скидка применится ко всем покупкам\n\n"
            "<b>Способ 2:</b> При оплате\n"
            "• Выберите тариф\n"
            "• Нажмите «🎁 Ввести промокод»\n"
            "• Введите код и увидите новую цену"
        )
    },
    {
        "id": "refund",
        "question": "💸 Можно ли вернуть деньги?",
        "answer": (
            "Возврат средств возможен в следующих случаях:\n\n"
            "• Технические проблемы с доступом\n"
            "• Канал прекратил работу\n"
            "• Двойное списание\n\n"
            "Для возврата обратитесь в поддержку с:\n"
            "• Номером транзакции из CryptoBot\n"
            "• Описанием проблемы\n"
            "• Вашим Telegram ID"
        )
    },
    {
        "id": "kicked",
        "question": "🚫 Меня удалили из канала",
        "answer": (
            "Возможные причины:\n\n"
            "• Истёк срок подписки — проверьте в «📋 Мои подписки»\n"
            "• Нарушение правил канала\n"
            "• Технический сбой\n\n"
            "Если подписка активна, но доступа нет — обратитесь в поддержку."
        )
    }
]


@router.message(F.text == "💬 Поддержка")
async def show_support(message: Message, bot_config: Dict[str, Any] = None):
    """Показать меню поддержки"""
    bot_config = bot_config or {}
    support_url = bot_config.get("support_url")
    
    builder = InlineKeyboardBuilder()
    
    # Кнопки FAQ
    builder.button(text="❓ Частые вопросы (FAQ)", callback_data="support_faq")
    
    # Кнопка связи с поддержкой
    if support_url:
        builder.button(text="✉️ Написать в поддержку", url=support_url)
    else:
        builder.button(text="✉️ Задать вопрос", callback_data="support_contact")
    
    # Информация об аккаунте
    builder.button(text="ℹ️ Информация о моём аккаунте", callback_data="support_account")
    
    builder.adjust(1)
    
    text = (
        "💬 <b>Поддержка</b>\n\n"
        "Как мы можем вам помочь?\n\n"
        "📚 Рекомендуем начать с <b>FAQ</b> — там ответы на большинство вопросов."
    )
    
    if support_url:
        text += f"\n\n👉 Или свяжитесь с нами напрямую"
    
    await message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")


@router.callback_query(F.data == "support_faq")
async def show_faq(callback: CallbackQuery):
    """Показать FAQ"""
    await callback.answer()
    
    builder = InlineKeyboardBuilder()
    
    for item in FAQ_ITEMS:
        builder.button(
            text=item["question"],
            callback_data=f"faq:{item['id']}"
        )
    
    builder.button(text="◀️ Назад", callback_data="support_back")
    builder.adjust(1)
    
    await callback.message.edit_text(
        "❓ <b>Частые вопросы (FAQ)</b>\n\n"
        "Выберите интересующий вопрос:",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("faq:"))
async def show_faq_answer(callback: CallbackQuery):
    """Показать ответ на FAQ"""
    await callback.answer()
    
    faq_id = callback.data.split(":")[1]
    
    # Находим вопрос
    faq_item = next((item for item in FAQ_ITEMS if item["id"] == faq_id), None)
    
    if not faq_item:
        await callback.answer("Вопрос не найден", show_alert=True)
        return
    
    builder = InlineKeyboardBuilder()
    builder.button(text="◀️ Назад к FAQ", callback_data="support_faq")
    builder.button(text="🏠 В поддержку", callback_data="support_back")
    builder.adjust(1)
    
    text = (
        f"<b>{faq_item['question']}</b>\n\n"
        f"{faq_item['answer']}"
    )
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")


@router.callback_query(F.data == "support_account")
async def show_account_info(callback: CallbackQuery):
    """Показать информацию об аккаунте пользователя"""
    await callback.answer()
    
    user = await get_user_by_telegram_id(callback.from_user.id)
    
    builder = InlineKeyboardBuilder()
    builder.button(text="◀️ Назад", callback_data="support_back")
    
    if not user:
        await callback.message.edit_text(
            "❌ Информация о вашем аккаунте не найдена.\n"
            "Нажмите /start для регистрации.",
            reply_markup=builder.as_markup()
        )
        return
    
    # Получаем подписки
    subscriptions = await get_user_subscriptions(user["id"], active_only=False)
    active_subs = [s for s in subscriptions if s.get("is_active")]
    
    # Форматируем дату регистрации
    created_at = user.get("created_at", "")
    if created_at:
        from datetime import datetime
        try:
            reg_date = datetime.fromisoformat(created_at)
            reg_str = reg_date.strftime("%d.%m.%Y %H:%M")
        except:
            reg_str = created_at
    else:
        reg_str = "Неизвестно"
    
    # Форматируем последнюю активность
    last_activity = user.get("last_activity", "")
    if last_activity:
        try:
            act_date = datetime.fromisoformat(last_activity)
            act_str = act_date.strftime("%d.%m.%Y %H:%M")
        except:
            act_str = last_activity
    else:
        act_str = "Неизвестно"
    
    text = (
        "ℹ️ <b>Информация об аккаунте</b>\n\n"
        f"🆔 <b>Telegram ID:</b> <code>{user['telegram_id']}</code>\n"
        f"👤 <b>Username:</b> @{user.get('username') or 'не указан'}\n"
        f"📛 <b>Имя:</b> {user.get('first_name') or 'не указано'}\n"
        f"📅 <b>Регистрация:</b> {reg_str}\n"
        f"🕐 <b>Последняя активность:</b> {act_str}\n\n"
        f"📊 <b>Статистика:</b>\n"
        f"• Активных подписок: {len(active_subs)}\n"
        f"• Всего подписок: {len(subscriptions)}\n\n"
        "💡 <i>ID может понадобиться при обращении в поддержку</i>"
    )
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")


@router.callback_query(F.data == "support_contact")
async def request_support_message(callback: CallbackQuery, state: FSMContext, bot_config: Dict[str, Any] = None):
    """Запросить сообщение для поддержки (если нет прямой ссылки)"""
    bot_config = bot_config or {}
    support_url = bot_config.get("support_url")
    
    if support_url:
        await callback.answer("Напишите в поддержку по ссылке", show_alert=True)
        return
    
    await callback.answer()
    
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Отмена", callback_data="support_back")
    
    await callback.message.edit_text(
        "✉️ <b>Обращение в поддержку</b>\n\n"
        "К сожалению, прямая ссылка на поддержку не настроена.\n\n"
        "Для решения вопроса, пожалуйста:\n"
        "1. Сохраните ваш Telegram ID (выше)\n"
        "2. Опишите проблему администратору канала\n"
        "3. Приложите скриншоты при необходимости",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "support_back")
async def back_to_support_menu(callback: CallbackQuery, bot_config: Dict[str, Any] = None):
    """Возврат в меню поддержки"""
    await callback.answer()
    
    bot_config = bot_config or {}
    support_url = bot_config.get("support_url")
    
    builder = InlineKeyboardBuilder()
    
    builder.button(text="❓ Частые вопросы (FAQ)", callback_data="support_faq")
    
    if support_url:
        builder.button(text="✉️ Написать в поддержку", url=support_url)
    else:
        builder.button(text="✉️ Задать вопрос", callback_data="support_contact")
    
    builder.button(text="ℹ️ Информация о моём аккаунте", callback_data="support_account")
    
    builder.adjust(1)
    
    text = (
        "💬 <b>Поддержка</b>\n\n"
        "Как мы можем вам помочь?\n\n"
        "📚 Рекомендуем начать с <b>FAQ</b> — там ответы на большинство вопросов."
    )
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
