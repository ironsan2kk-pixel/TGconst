"""Database initialization script with default texts."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from bot.config import config
from bot.database import engine, async_session_factory
from bot.models import Base, Text, Settings, FAQItem


# Default texts for bot
DEFAULT_TEXTS = [
    # === Messages ===
    {
        "key": "welcome",
        "category": "messages",
        "text_ru": "👋 Добро пожаловать!\n\nЯ помогу вам получить доступ к приватным каналам.\n\nВыберите действие в меню ниже:",
        "text_en": "👋 Welcome!\n\nI will help you get access to private channels.\n\nChoose an action from the menu below:",
        "description": "Приветственное сообщение",
        "variables": "{first_name}, {username}"
    },
    {
        "key": "language_prompt",
        "category": "messages",
        "text_ru": "🌐 Выберите язык:",
        "text_en": "🌐 Choose language:",
        "description": "Выбор языка"
    },
    {
        "key": "language_changed",
        "category": "messages",
        "text_ru": "✅ Язык изменён на русский",
        "text_en": "✅ Language changed to English",
        "description": "Язык изменён"
    },
    {
        "key": "packages_list",
        "category": "messages",
        "text_ru": "📦 Доступные пакеты:",
        "text_en": "📦 Available packages:",
        "description": "Заголовок списка пакетов"
    },
    {
        "key": "package_details",
        "category": "messages",
        "text_ru": "📦 <b>{name}</b>\n\n{description}\n\n📺 Каналы: {channels_count}\n\nВыберите срок подписки:",
        "text_en": "📦 <b>{name}</b>\n\n{description}\n\n📺 Channels: {channels_count}\n\nChoose subscription period:",
        "description": "Детали пакета",
        "variables": "{name}, {description}, {channels_count}"
    },
    {
        "key": "payment_prompt",
        "category": "messages",
        "text_ru": "💳 <b>Оплата</b>\n\n📦 Пакет: {package_name}\n⏱ Срок: {duration}\n💰 Сумма: <b>{amount} USDT</b>\n\n🔗 Адрес кошелька:\n<code>{wallet}</code>\n\n📤 После оплаты отправьте hash транзакции в этот чат.",
        "text_en": "💳 <b>Payment</b>\n\n📦 Package: {package_name}\n⏱ Duration: {duration}\n💰 Amount: <b>{amount} USDT</b>\n\n🔗 Wallet address:\n<code>{wallet}</code>\n\n📤 After payment, send the transaction hash to this chat.",
        "description": "Инструкция по оплате",
        "variables": "{package_name}, {duration}, {amount}, {wallet}"
    },
    {
        "key": "payment_checking",
        "category": "messages",
        "text_ru": "🔍 Проверяю транзакцию...",
        "text_en": "🔍 Checking transaction...",
        "description": "Проверка транзакции"
    },
    {
        "key": "payment_success",
        "category": "messages",
        "text_ru": "✅ Оплата подтверждена!\n\nВаша подписка активирована.",
        "text_en": "✅ Payment confirmed!\n\nYour subscription is now active.",
        "description": "Оплата прошла"
    },
    {
        "key": "payment_failed",
        "category": "messages",
        "text_ru": "❌ Транзакция не найдена.\n\nПроверьте hash и попробуйте снова или обратитесь в поддержку.",
        "text_en": "❌ Transaction not found.\n\nPlease check the hash and try again or contact support.",
        "description": "Оплата не найдена"
    },
    {
        "key": "subscription_active",
        "category": "messages",
        "text_ru": "✅ <b>Подписка активирована!</b>\n\n📦 Пакет: {package_name}\n⏱ До: {expires_at}\n\nСсылки на каналы доступны в разделе \"Мои подписки\".",
        "text_en": "✅ <b>Subscription activated!</b>\n\n📦 Package: {package_name}\n⏱ Until: {expires_at}\n\nChannel links are available in \"My subscriptions\" section.",
        "description": "Подписка активирована",
        "variables": "{package_name}, {expires_at}"
    },
    {
        "key": "my_subscriptions",
        "category": "messages",
        "text_ru": "💳 <b>Мои подписки:</b>",
        "text_en": "💳 <b>My subscriptions:</b>",
        "description": "Заголовок моих подписок"
    },
    {
        "key": "no_subscriptions",
        "category": "messages",
        "text_ru": "У вас пока нет активных подписок.\n\nВыберите пакет в разделе \"Пакеты\".",
        "text_en": "You don't have any active subscriptions yet.\n\nChoose a package in the \"Packages\" section.",
        "description": "Нет подписок"
    },
    {
        "key": "subscription_info",
        "category": "messages",
        "text_ru": "📦 <b>{package_name}</b>\n✅ Статус: Активна\n⏱ До: {expires_at}\n📅 Осталось: {days_left} дн.",
        "text_en": "📦 <b>{package_name}</b>\n✅ Status: Active\n⏱ Until: {expires_at}\n📅 Remaining: {days_left} days",
        "description": "Информация о подписке",
        "variables": "{package_name}, {expires_at}, {days_left}"
    },
    {
        "key": "subscription_expiring_3d",
        "category": "notifications",
        "text_ru": "⚠️ Ваша подписка на <b>{package_name}</b> истекает через 3 дня.\n\nПродлите сейчас, чтобы не потерять доступ!",
        "text_en": "⚠️ Your subscription to <b>{package_name}</b> expires in 3 days.\n\nRenew now to keep your access!",
        "description": "Напоминание за 3 дня",
        "variables": "{package_name}"
    },
    {
        "key": "subscription_expiring_1d",
        "category": "notifications",
        "text_ru": "⚠️ Ваша подписка на <b>{package_name}</b> истекает завтра!\n\nПродлите сейчас, чтобы не потерять доступ!",
        "text_en": "⚠️ Your subscription to <b>{package_name}</b> expires tomorrow!\n\nRenew now to keep your access!",
        "description": "Напоминание за 1 день",
        "variables": "{package_name}"
    },
    {
        "key": "subscription_expired",
        "category": "notifications",
        "text_ru": "❌ Ваша подписка на <b>{package_name}</b> истекла.\n\nВы были удалены из каналов. Оформите новую подписку для восстановления доступа.",
        "text_en": "❌ Your subscription to <b>{package_name}</b> has expired.\n\nYou have been removed from channels. Get a new subscription to restore access.",
        "description": "Подписка истекла",
        "variables": "{package_name}"
    },
    {
        "key": "trial_started",
        "category": "messages",
        "text_ru": "🎉 Пробный период активирован!\n\n📦 Пакет: {package_name}\n⏱ Срок: {trial_days} дней\n\nНаслаждайтесь доступом!",
        "text_en": "🎉 Trial period activated!\n\n📦 Package: {package_name}\n⏱ Duration: {trial_days} days\n\nEnjoy your access!",
        "description": "Пробный период начат",
        "variables": "{package_name}, {trial_days}"
    },
    {
        "key": "trial_not_available",
        "category": "messages",
        "text_ru": "❌ Пробный период недоступен.\n\nВы уже использовали пробный период ранее.",
        "text_en": "❌ Trial is not available.\n\nYou have already used your trial period.",
        "description": "Пробный недоступен"
    },
    {
        "key": "promocode_prompt",
        "category": "messages",
        "text_ru": "🎁 Введите промокод:",
        "text_en": "🎁 Enter promocode:",
        "description": "Ввод промокода"
    },
    {
        "key": "promocode_applied",
        "category": "messages",
        "text_ru": "✅ Промокод применён!\n\n💰 Скидка: {discount}\n💵 Новая цена: {new_price} USDT",
        "text_en": "✅ Promocode applied!\n\n💰 Discount: {discount}\n💵 New price: {new_price} USDT",
        "description": "Промокод применён",
        "variables": "{discount}, {new_price}"
    },
    {
        "key": "promocode_invalid",
        "category": "messages",
        "text_ru": "❌ Неверный или недействительный промокод.",
        "text_en": "❌ Invalid or expired promocode.",
        "description": "Неверный промокод"
    },
    {
        "key": "faq_title",
        "category": "messages",
        "text_ru": "❓ <b>Часто задаваемые вопросы:</b>",
        "text_en": "❓ <b>Frequently asked questions:</b>",
        "description": "Заголовок FAQ"
    },
    {
        "key": "user_banned",
        "category": "messages",
        "text_ru": "🚫 Вы заблокированы.\n\nПричина: {reason}\n\nОбратитесь в поддержку.",
        "text_en": "🚫 You are banned.\n\nReason: {reason}\n\nPlease contact support.",
        "description": "Пользователь забанен",
        "variables": "{reason}"
    },
    
    # === Buttons ===
    {
        "key": "btn_packages",
        "category": "buttons",
        "text_ru": "📦 Пакеты",
        "text_en": "📦 Packages",
        "description": "Кнопка пакетов"
    },
    {
        "key": "btn_subscriptions",
        "category": "buttons",
        "text_ru": "💳 Мои подписки",
        "text_en": "💳 My subscriptions",
        "description": "Кнопка подписок"
    },
    {
        "key": "btn_promocode",
        "category": "buttons",
        "text_ru": "🎁 Промокод",
        "text_en": "🎁 Promocode",
        "description": "Кнопка промокода"
    },
    {
        "key": "btn_faq",
        "category": "buttons",
        "text_ru": "❓ FAQ",
        "text_en": "❓ FAQ",
        "description": "Кнопка FAQ"
    },
    {
        "key": "btn_language",
        "category": "buttons",
        "text_ru": "🌐 Язык",
        "text_en": "🌐 Language",
        "description": "Кнопка языка"
    },
    {
        "key": "btn_support",
        "category": "buttons",
        "text_ru": "💬 Поддержка",
        "text_en": "💬 Support",
        "description": "Кнопка поддержки"
    },
    {
        "key": "btn_back",
        "category": "buttons",
        "text_ru": "⬅️ Назад",
        "text_en": "⬅️ Back",
        "description": "Кнопка назад"
    },
    {
        "key": "btn_pay",
        "category": "buttons",
        "text_ru": "💳 Оплатить",
        "text_en": "💳 Pay",
        "description": "Кнопка оплаты"
    },
    {
        "key": "btn_cancel",
        "category": "buttons",
        "text_ru": "❌ Отмена",
        "text_en": "❌ Cancel",
        "description": "Кнопка отмены"
    },
    {
        "key": "btn_renew",
        "category": "buttons",
        "text_ru": "🔄 Продлить",
        "text_en": "🔄 Renew",
        "description": "Кнопка продления"
    },
    {
        "key": "btn_links",
        "category": "buttons",
        "text_ru": "🔗 Ссылки на каналы",
        "text_en": "🔗 Channel links",
        "description": "Кнопка ссылок"
    },
    {
        "key": "btn_trial",
        "category": "buttons",
        "text_ru": "🎁 Пробный период",
        "text_en": "🎁 Free trial",
        "description": "Кнопка пробного периода"
    },
    
    # === Admin notifications ===
    {
        "key": "admin_new_user",
        "category": "notifications",
        "text_ru": "👤 <b>Новый пользователь</b>\n\nID: {telegram_id}\nИмя: {first_name}\nUsername: @{username}",
        "text_en": "👤 <b>New user</b>\n\nID: {telegram_id}\nName: {first_name}\nUsername: @{username}",
        "description": "Уведомление о новом юзере",
        "variables": "{telegram_id}, {first_name}, {username}"
    },
    {
        "key": "admin_new_payment",
        "category": "notifications",
        "text_ru": "💰 <b>Новая оплата</b>\n\nПользователь: {user_name}\nПакет: {package_name}\nСумма: {amount} USDT\nСеть: {network}",
        "text_en": "💰 <b>New payment</b>\n\nUser: {user_name}\nPackage: {package_name}\nAmount: {amount} USDT\nNetwork: {network}",
        "description": "Уведомление о новой оплате",
        "variables": "{user_name}, {package_name}, {amount}, {network}"
    },
]


# Default settings
DEFAULT_SETTINGS = {
    "support_url": "https://t.me/support",
    "default_language": "ru",
    "notify_new_users": "true",
    "notify_payments": "true",
    "payment_timeout_min": "30",
    "promocode_enabled": "true",
    "trial_enabled": "true",
    "ton_wallet": "",
    "trc20_wallet": "",
}


# Default FAQ items
DEFAULT_FAQ = [
    {
        "question_ru": "Как оплатить подписку?",
        "question_en": "How to pay for subscription?",
        "answer_ru": "1. Выберите пакет и срок подписки\n2. Выберите сеть оплаты (TON или TRC20)\n3. Переведите указанную сумму на кошелёк\n4. Отправьте hash транзакции боту",
        "answer_en": "1. Choose a package and subscription period\n2. Select payment network (TON or TRC20)\n3. Transfer the specified amount to the wallet\n4. Send the transaction hash to the bot",
        "sort_order": 1,
    },
    {
        "question_ru": "Как получить доступ к каналам после оплаты?",
        "question_en": "How to get access to channels after payment?",
        "answer_ru": "После подтверждения оплаты бот автоматически добавит вас во все каналы пакета. Ссылки также будут доступны в разделе \"Мои подписки\".",
        "answer_en": "After payment confirmation, the bot will automatically add you to all package channels. Links will also be available in \"My subscriptions\" section.",
        "sort_order": 2,
    },
    {
        "question_ru": "Что будет когда подписка истечёт?",
        "question_en": "What happens when subscription expires?",
        "answer_ru": "За 3 дня и за 1 день до окончания вы получите напоминание. После истечения подписки вы будете автоматически удалены из каналов.",
        "answer_en": "You will receive reminders 3 days and 1 day before expiration. After subscription expires, you will be automatically removed from channels.",
        "sort_order": 3,
    },
]


async def setup_database() -> None:
    """Initialize database with tables and default data."""
    print("🔧 Initializing database...")
    
    # Ensure data directory exists
    config.ensure_dirs()
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tables created")
    
    # Add default data
    async with async_session_factory() as session:
        # Check if texts exist
        from sqlalchemy import select
        result = await session.execute(select(Text).limit(1))
        if result.scalar_one_or_none() is None:
            print("📝 Adding default texts...")
            for text_data in DEFAULT_TEXTS:
                text = Text(**text_data)
                session.add(text)
            await session.commit()
            print(f"✅ Added {len(DEFAULT_TEXTS)} default texts")
        else:
            print("ℹ️ Texts already exist, skipping")
        
        # Check if settings exist
        result = await session.execute(select(Settings).limit(1))
        if result.scalar_one_or_none() is None:
            print("⚙️ Adding default settings...")
            for key, value in DEFAULT_SETTINGS.items():
                setting = Settings(key=key, value=value)
                session.add(setting)
            await session.commit()
            print(f"✅ Added {len(DEFAULT_SETTINGS)} default settings")
        else:
            print("ℹ️ Settings already exist, skipping")
        
        # Check if FAQ exists
        result = await session.execute(select(FAQItem).limit(1))
        if result.scalar_one_or_none() is None:
            print("❓ Adding default FAQ...")
            for faq_data in DEFAULT_FAQ:
                faq = FAQItem(**faq_data)
                session.add(faq)
            await session.commit()
            print(f"✅ Added {len(DEFAULT_FAQ)} FAQ items")
        else:
            print("ℹ️ FAQ already exists, skipping")
    
    print("\n✅ Database initialization complete!")
    print(f"📁 Database file: {config.database_path}")


if __name__ == "__main__":
    asyncio.run(setup_database())
