"""
Сервисы бота.
"""

from bot.services.notifications import notify_new_user, notify_admins
from bot.services.cryptobot import cryptobot, CryptoBotAPI, CryptoBotError
from bot.services.subscription import (
    create_subscription,
    get_active_subscription,
    get_user_subscriptions,
    deactivate_subscription,
    get_tariff_channels,
    check_user_has_trial,
    extend_subscription,
)


__all__ = [
    # Notifications
    'notify_new_user',
    'notify_admins',
    # CryptoBot
    'cryptobot',
    'CryptoBotAPI',
    'CryptoBotError',
    # Subscriptions
    'create_subscription',
    'get_active_subscription',
    'get_user_subscriptions',
    'deactivate_subscription',
    'get_tariff_channels',
    'check_user_has_trial',
    'extend_subscription',
]
