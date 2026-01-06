"""
Inline клавиатуры бота.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.locales import get_text, get_language_name, get_available_languages
from bot.models import Tariff


def language_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора языка."""
    builder = InlineKeyboardBuilder()
    
    for lang in get_available_languages():
        builder.button(
            text=get_language_name(lang),
            callback_data=f"lang:{lang}"
        )
    
    builder.adjust(2)
    return builder.as_markup()


def main_menu_keyboard(lang: str, has_subscription: bool = False) -> InlineKeyboardMarkup:
    """Главное меню бота."""
    builder = InlineKeyboardBuilder()
    
    _ = lambda key: get_text(key, lang)
    
    # Тарифы (показываем если нет подписки)
    if not has_subscription:
        builder.button(
            text=_('menu.tariffs'),
            callback_data="menu:tariffs"
        )
    
    # Мои подписки
    builder.button(
        text=_('menu.my_subscriptions'),
        callback_data="menu:subscriptions"
    )
    
    # Промокод
    builder.button(
        text=_('menu.promocode'),
        callback_data="menu:promocode"
    )
    
    # Язык
    builder.button(
        text=_('menu.language'),
        callback_data="menu:language"
    )
    
    # Поддержка
    builder.button(
        text=_('menu.support'),
        callback_data="menu:support"
    )
    
    # Располагаем кнопки
    if not has_subscription:
        builder.adjust(1, 2, 2)
    else:
        builder.adjust(1, 2, 2)
    
    return builder.as_markup()


def tariffs_keyboard(
    tariffs: list[Tariff], 
    lang: str
) -> InlineKeyboardMarkup:
    """Список тарифов."""
    builder = InlineKeyboardBuilder()
    
    _ = lambda key, **kw: get_text(key, lang, **kw)
    
    for tariff in tariffs:
        name = tariff.name_ru if lang == 'ru' else tariff.name_en
        price = f"{tariff.price:.2f}" if tariff.price else "0.00"
        
        builder.button(
            text=f"{name} — {price} USDT",
            callback_data=f"tariff:{tariff.id}"
        )
    
    # Кнопка назад
    builder.button(
        text=_('menu.back'),
        callback_data="menu:main"
    )
    
    builder.adjust(1)
    return builder.as_markup()


def tariff_detail_keyboard(
    tariff: Tariff,
    lang: str,
    has_trial: bool = False,
) -> InlineKeyboardMarkup:
    """Детали тарифа с кнопкой покупки."""
    builder = InlineKeyboardBuilder()
    
    _ = lambda key, **kw: get_text(key, lang, **kw)
    
    # Кнопка покупки
    if tariff.trial_days and tariff.trial_days > 0 and has_trial:
        builder.button(
            text=_('tariffs.buy_trial'),
            callback_data=f"buy_trial:{tariff.id}"
        )
    
    builder.button(
        text=_('tariffs.buy'),
        callback_data=f"buy:{tariff.id}"
    )
    
    # Назад к списку
    builder.button(
        text=_('tariffs.back_to_list'),
        callback_data="menu:tariffs"
    )
    
    builder.adjust(1)
    return builder.as_markup()


def back_to_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Кнопка возврата в меню."""
    builder = InlineKeyboardBuilder()
    
    builder.button(
        text=get_text('menu.back', lang),
        callback_data="menu:main"
    )
    
    return builder.as_markup()


def payment_keyboard(
    invoice_url: str,
    invoice_id: str,
    amount: float,
    lang: str,
) -> InlineKeyboardMarkup:
    """Клавиатура оплаты."""
    builder = InlineKeyboardBuilder()
    
    _ = lambda key, **kw: get_text(key, lang, **kw)
    
    # Кнопка оплаты (ссылка на CryptoBot)
    builder.button(
        text=_('payment.pay_button', amount=f"{amount:.2f}"),
        url=invoice_url
    )
    
    # Проверить оплату
    builder.button(
        text=_('payment.check_payment'),
        callback_data=f"check_payment:{invoice_id}"
    )
    
    # Отмена
    builder.button(
        text=_('payment.cancel'),
        callback_data=f"cancel_payment:{invoice_id}"
    )
    
    builder.adjust(1)
    return builder.as_markup()


def support_keyboard(support_url: str, lang: str) -> InlineKeyboardMarkup:
    """Клавиатура поддержки."""
    builder = InlineKeyboardBuilder()
    
    _ = lambda key: get_text(key, lang)
    
    if support_url:
        builder.button(
            text=_('support.button'),
            url=support_url
        )
    
    builder.button(
        text=_('menu.back'),
        callback_data="menu:main"
    )
    
    builder.adjust(1)
    return builder.as_markup()
