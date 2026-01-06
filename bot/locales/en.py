"""
English localization for the bot.
"""

TEXTS = {
    # General
    'welcome': '👋 Welcome!\n\nВыберите язык / Choose language:',
    'welcome_back': '👋 Welcome back, {name}!',
    'choose_language': '🌐 Choose language:',
    'language_changed': '✅ Language changed to English',
    'error': '❌ An error occurred. Please try again later.',
    'banned': '🚫 You are blocked.\n\nReason: {reason}',
    'rate_limit': '⏳ Too many requests. Please wait a moment.',
    
    # Main menu
    'menu': {
        'title': '📱 Main Menu',
        'tariffs': '📺 Plans',
        'my_subscriptions': '💳 My Subscriptions',
        'promocode': '🎁 Promo Code',
        'language': '🌐 Language',
        'support': '💬 Support',
        'back': '◀️ Back',
    },
    
    # Tariffs
    'tariffs': {
        'title': '📺 Available Plans',
        'empty': '😔 No plans available',
        'detail': (
            '📦 <b>{name}</b>\n\n'
            '{description}\n\n'
            '💰 Price: <b>{price} USDT</b>\n'
            '⏱ Duration: <b>{duration}</b>\n'
            '{trial}'
            '\n📺 Channels:\n{channels}'
        ),
        'duration_days': '{days} days',
        'duration_forever': 'Forever',
        'trial_info': '🎁 Free trial: {days} days\n',
        'buy': '💳 Buy',
        'buy_trial': '🎁 Try for Free',
        'back_to_list': '◀️ Back to Plans',
    },
    
    # Payment
    'payment': {
        'creating': '⏳ Creating payment invoice...',
        'invoice_created': (
            '💳 <b>Payment Invoice</b>\n\n'
            '📦 Plan: {tariff}\n'
            '💰 Amount: <b>{amount} USDT</b>\n'
            '{discount}'
            '\n⏱ Invoice valid for 60 minutes\n\n'
            '👇 Click the button to pay:'
        ),
        'discount_applied': '🎁 Discount: -{discount} USDT\n',
        'pay_button': '💳 Pay {amount} USDT',
        'check_payment': '🔄 Check Payment',
        'cancel': '❌ Cancel',
        'success': (
            '✅ <b>Payment Successful!</b>\n\n'
            '📦 Plan: {tariff}\n'
            '⏱ Active until: {expires}\n\n'
            '🔗 Channel links are sent below.'
        ),
        'success_forever': (
            '✅ <b>Payment Successful!</b>\n\n'
            '📦 Plan: {tariff}\n'
            '⏱ Duration: Forever\n\n'
            '🔗 Channel links are sent below.'
        ),
        'expired': '❌ Invoice expired. Please create a new one.',
        'cancelled': '❌ Payment cancelled.',
        'pending': '⏳ Payment not received yet. Please try again later.',
        'already_paid': '✅ This invoice has already been paid.',
        'cryptobot_disabled': '❌ Payments are temporarily unavailable.',
        'channel_link': '📺 {title}: {link}',
    },
    
    # Subscriptions
    'subscriptions': {
        'title': '💳 My Subscriptions',
        'empty': '😔 You have no active subscriptions',
        'item': (
            '📦 <b>{tariff}</b>\n'
            '⏱ Active until: {expires}\n'
            '📺 Channels: {channels_count}'
        ),
        'item_forever': (
            '📦 <b>{tariff}</b>\n'
            '⏱ Duration: Forever\n'
            '📺 Channels: {channels_count}'
        ),
        'item_trial': ' (trial period)',
        'expiring_soon': '⚠️ Expiring soon!',
        'detail': (
            '📦 <b>{tariff}</b>\n\n'
            '📅 Started: {starts}\n'
            '⏱ Expires: {expires}\n'
            '📺 Channels: {channels_count}\n'
            '{status}'
        ),
        'status_active': '✅ Active',
        'status_trial': '🎁 Trial period',
        'status_expiring': '⚠️ Expiring soon',
    },
    
    # Subscription (для уведомлений)
    'subscription': {
        'renew_button': '🔄 Renew Subscription',
        'back_to_list': '◀️ Back to Subscriptions',
    },
    
    # Уведомления о подписках
    'subscription_expires_3days': (
        '⏰ <b>Reminder</b>\n\n'
        'Your subscription "{tariff_name}" expires in 3 days.\n'
        '📅 Expiration date: {expires_at}\n\n'
        '👇 Renew your subscription to keep access.'
    ),
    'subscription_expires_1day': (
        '⚠️ <b>Attention!</b>\n\n'
        'Your subscription "{tariff_name}" expires tomorrow!\n'
        '📅 Expiration date: {expires_at}\n\n'
        '👇 Renew your subscription now.'
    ),
    'subscription_expired': (
        '❌ <b>Subscription Expired</b>\n\n'
        'Your subscription "{tariff_name}" has ended.\n'
        'Access to channels has been revoked.\n\n'
        '👇 Purchase a new subscription to regain access.'
    ),
    
    # Promo codes
    'promocode': {
        'enter': '🎁 Enter promo code:',
        'applied': '✅ Promo code applied! Discount: {discount}',
        'invalid': '❌ Invalid promo code',
        'expired': '❌ Promo code has expired',
        'already_used': '❌ You have already used this promo code',
        'limit_reached': '❌ Promo code usage limit reached',
    },
    
    # Notifications (старые, для совместимости)
    'notifications': {
        'subscription_expires_3days': (
            '⏰ <b>Reminder</b>\n\n'
            'Your subscription "{tariff}" expires in 3 days.\n\n'
            '👇 Renew your subscription to keep access.'
        ),
        'subscription_expires_1day': (
            '⚠️ <b>Attention!</b>\n\n'
            'Your subscription "{tariff}" expires tomorrow!\n\n'
            '👇 Renew your subscription now.'
        ),
        'subscription_expired': (
            '❌ <b>Subscription Expired</b>\n\n'
            'Your subscription "{tariff}" has ended.\n'
            'Access to channels has been revoked.\n\n'
            '👇 Purchase a new subscription to regain access.'
        ),
        'renew': '🔄 Renew',
    },
    
    # Support
    'support': {
        'text': (
            '💬 <b>Support</b>\n\n'
            'If you have any questions, contact us:'
        ),
        'button': '💬 Contact Support',
    },
    
    # Admin notifications
    'admin': {
        'new_user': (
            '👤 <b>New User</b>\n\n'
            'ID: <code>{user_id}</code>\n'
            'Name: {name}\n'
            'Username: @{username}\n'
            'Language: {language}'
        ),
        'new_payment': (
            '💰 <b>New Payment</b>\n\n'
            'User: {name} (@{username})\n'
            'ID: <code>{user_id}</code>\n'
            'Plan: {tariff}\n'
            'Amount: {amount} USDT'
        ),
    },
    
    # Buttons
    'buttons': {
        'yes': '✅ Yes',
        'no': '❌ No',
        'cancel': '❌ Cancel',
        'back': '◀️ Back',
        'confirm': '✅ Confirm',
    },
}
