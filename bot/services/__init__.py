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
from bot.services.subscription_checker import (
    SubscriptionChecker,
    run_single_check,
)
from bot.services.promocode import (
    get_promocode,
    validate_promocode,
    apply_promocode,
    format_discount,
    PromocodeError,
    PromocodeNotFoundError,
    PromocodeExpiredError,
    PromocodeAlreadyUsedError,
    PromocodeLimitReachedError,
    PromocodeNotApplicableError,
)
from bot.services.broadcast import (
    create_broadcast,
    get_broadcast,
    update_broadcast,
    delete_broadcast,
    start_broadcast,
    pause_broadcast,
    resume_broadcast,
    cancel_broadcast,
    get_broadcasts_list,
    count_broadcast_recipients,
    get_broadcast_recipients,
    quick_broadcast,
    parse_buttons,
    BroadcastError,
    BroadcastNotFoundError,
    BroadcastInvalidStateError,
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
    # Subscription Checker
    'SubscriptionChecker',
    'run_single_check',
    # Promocodes
    'get_promocode',
    'validate_promocode',
    'apply_promocode',
    'format_discount',
    'PromocodeError',
    'PromocodeNotFoundError',
    'PromocodeExpiredError',
    'PromocodeAlreadyUsedError',
    'PromocodeLimitReachedError',
    'PromocodeNotApplicableError',
    # Broadcasts
    'create_broadcast',
    'get_broadcast',
    'update_broadcast',
    'delete_broadcast',
    'start_broadcast',
    'pause_broadcast',
    'resume_broadcast',
    'cancel_broadcast',
    'get_broadcasts_list',
    'count_broadcast_recipients',
    'get_broadcast_recipients',
    'quick_broadcast',
    'parse_buttons',
    'BroadcastError',
    'BroadcastNotFoundError',
    'BroadcastInvalidStateError',
]
