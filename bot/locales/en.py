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
    'rate_limit': '⏳ Too many requests. Please wait.',
    
    # Reply Keyboard
    'reply': {
        'get_access': '🚀 Get access',
        'my_subscriptions': '💳 My subscriptions',
        'settings': '⚙️ Settings',
        'contacts': '📞 Contacts',
        'promocode': '🎁 Promocode',
    },
    
    # Main menu
    'menu': {
        'title': '📱 Main menu',
        'tariffs': '📺 Plans',
        'my_subscriptions': '💳 My subscriptions',
        'promocode': '🎁 Promocode',
        'language': '🌐 Language',
        'support': '💬 Support',
        'back': 'Back',
        'settings': '⚙️ Settings',
        'contacts': '📞 Contacts',
    },
    
    # Tariffs
    'tariffs': {
        'title': '📦 Choose a plan:',
        'empty': '😔 No available plans',
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
        'trial_info': '🎁 Trial period: {days} days\n',
        'buy': '💳 Buy',
        'buy_trial': '🎁 Try for free',
        'back_to_list': '◀️ Back to list',
    },
    
    # Payment
    'payment': {
        'creating': '⏳ Creating invoice...',
        'invoice_created': (
            '💳 <b>Payment Invoice</b>\n\n'
            '📦 Plan: {tariff}\n'
            '💰 Amount: <b>{amount} USDT</b>\n'
            '{discount}'
            '\n⏱ Invoice valid for 60 minutes\n\n'
            '👇 Click button to pay:'
        ),
        'discount_applied': '🎁 Discount: -{discount} USDT\n',
        'pay_button': '💳 Pay {amount} USDT',
        'check_payment': '🔄 Check payment',
        'cancel': '❌ Cancel',
        'success': (
            '✅ <b>Payment successful!</b>\n\n'
            '📦 Plan: {tariff}\n'
            '⏱ Active until: {expires}\n\n'
            '🔗 Channel links sent below.'
        ),
        'success_forever': (
            '✅ <b>Payment successful!</b>\n\n'
            '📦 Plan: {tariff}\n'
            '⏱ Duration: Forever\n\n'
            '🔗 Channel links sent below.'
        ),
        'expired': '❌ Invoice expired. Create a new one.',
        'cancelled': '❌ Payment cancelled.',
        'pending': '⏳ Payment not received yet. Try again later.',
        'already_paid': '✅ This invoice is already paid.',
        'cryptobot_disabled': '❌ Payment temporarily unavailable.',
        'channel_link': '📺 {title}: {link}',
    },
    
    # Subscriptions
    'subscriptions': {
        'title': '📋 Your active subscriptions:',
        'empty': '😔 You have no active subscriptions',
        'item': (
            '✅ <b>{tariff}</b>\n'
            '   Until: {expires}'
        ),
        'item_forever': (
            '✅ <b>{tariff}</b>\n'
            '   Duration: Forever'
        ),
        'item_trial': ' (trial period)',
        'expiring_soon': '⚠️ Expiring soon!',
        'channels_header': '\n📺 Channels:',
        'channel_item': '• {title}',
        'detail': (
            '📦 <b>{tariff}</b>\n\n'
            '📅 Start: {starts}\n'
            '⏱ End: {expires}\n'
            '📺 Channels: {channels_count}\n'
            '{status}'
        ),
        'status_active': '✅ Active',
        'status_trial': '🎁 Trial period',
        'status_expiring': '⚠️ Expiring soon',
    },
    
    # Subscription (for notifications)
    'subscription': {
        'renew_button': '🔄 Renew subscription',
        'back_to_list': '◀️ Back to list',
    },
    
    # Subscription notifications
    'subscription_expires_3days': (
        '⏰ <b>Reminder</b>\n\n'
        'Your subscription "{tariff_name}" expires in 3 days.\n'
        '📅 Expiration date: {expires_at}\n\n'
        '👇 Renew to keep your access.'
    ),
    'subscription_expires_1day': (
        '⚠️ <b>Attention!</b>\n\n'
        'Your subscription "{tariff_name}" expires tomorrow!\n'
        '📅 Expiration date: {expires_at}\n\n'
        '👇 Renew now.'
    ),
    'subscription_expired': (
        '❌ <b>Subscription expired</b>\n\n'
        'Your subscription "{tariff_name}" has ended.\n'
        'Channel access has been revoked.\n\n'
        '👇 Get a new subscription to restore access.'
    ),
    
    # Promocodes
    'promocode': {
        'enter': '🎁 Enter promocode:\n\nSend the code as a message',
        'applied': '✅ Promocode applied! Discount: {discount}',
        'invalid': '❌ Invalid promocode',
        'expired': '❌ Promocode expired',
        'already_used': '❌ You already used this promocode',
        'limit_reached': '❌ Promocode usage limit reached',
    },
    
    # Contacts
    'contacts': {
        'title': '📞 Contacts',
        'admin': 'Admin: {admin}',
        'support': 'Support: {support}',
        'channel': 'Channel: {channel}',
    },
    
    # Settings
    'settings': {
        'title': '⚙️ Settings',
        'back': '🔙 Back',
    },
    
    # Notifications (old, for compatibility)
    'notifications': {
        'subscription_expires_3days': (
            '⏰ <b>Reminder</b>\n\n'
            'Your subscription "{tariff}" expires in 3 days.\n\n'
            '👇 Renew to keep your access.'
        ),
        'subscription_expires_1day': (
            '⚠️ <b>Attention!</b>\n\n'
            'Your subscription "{tariff}" expires tomorrow!\n\n'
            '👇 Renew now.'
        ),
        'subscription_expired': (
            '❌ <b>Subscription expired</b>\n\n'
            'Your subscription "{tariff}" has ended.\n'
            'Channel access has been revoked.\n\n'
            '👇 Get a new subscription to restore access.'
        ),
        'renew': '🔄 Renew',
    },
    
    # Support
    'support': {
        'text': (
            '💬 <b>Support</b>\n\n'
            'If you have questions, contact us:'
        ),
        'button': '💬 Contact support',
    },
    
    # Admin notifications
    'admin': {
        'new_user': (
            '👤 <b>New user</b>\n\n'
            'ID: <code>{user_id}</code>\n'
            'Name: {name}\n'
            'Username: @{username}\n'
            'Language: {language}'
        ),
        'new_payment': (
            '💰 <b>New payment</b>\n\n'
            'User: {name} (@{username})\n'
            'ID: <code>{user_id}</code>\n'
            'Plan: {tariff}\n'
            'Amount: {amount} USDT'
        ),
        # Admin panel
        'menu_title': '🔧 Admin Panel',
        'stats_title': '📊 Statistics',
        'total_users': 'Total users',
        'new_today': 'New today',
        'active_subs': 'Active subscriptions',
        'revenue_today': 'Revenue today',
        'revenue_month': 'Revenue this month',
        'search_user': '🔍 Search user',
        'grant_access': '➕ Grant access',
        'revoke_access': '➖ Revoke access',
        'ban_user': '🚫 Ban',
        'unban_user': '✅ Unban',
        'manual_payment': '💳 Manual payment',
        'broadcast': '📨 Broadcast',
        'user_not_found': 'User not found',
        'access_granted': 'Access granted',
        'access_revoked': 'Access revoked',
        'user_banned': 'User banned',
        'user_unbanned': 'User unbanned',
        'payment_confirmed': 'Payment confirmed',
        'broadcast_sent': 'Broadcast sent',
        'is_admin': 'You are an administrator!',
    },
    
    # FAQ
    'faq': {
        'title': '❓ Frequently Asked Questions',
        'empty': 'No questions yet',
        'select': 'Select a question:',
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
