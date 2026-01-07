# 🔧 МАСТЕР-ПЛАН: Telegram-бот продажи доступа к каналам

**Версия:** 4.0  
**Дата:** Январь 2025  
**Платформа:** Windows Server  
**Архитектура:** Один бот, SQLite, без Docker

---

## 📌 ОБЩЕЕ ОПИСАНИЕ

### Что это?
Telegram-бот для продажи доступа к приватным каналам через криптовалюту (TON/TRC20).

### Ключевые особенности:
- **Один бот** — фиксированный шаблон, надёжный и простой
- **Пакеты каналов** — один пакет = несколько каналов + варианты сроков (30/90/365 дней)
- **Два языка** — русский и английский с переключением
- **Пробный период** — 3/5/7 дней опционально для каждого варианта
- **Оплата криптой** — TON и TRC20 (USDT), проверка по hash транзакции
- **Тёмная тема** — в админке с переключателем
- **Контент-менеджер** — все тексты редактируются в админке
- **Графики аналитики** — доход, конверсия, активность
- **Напоминания** — о продлении подписки (за 3 дня, за 1 день)
- **Промокоды** — скидка % или фикс. сумма
- **Рассылки** — с фильтрами по юзерам

### НЕ включено:
- ❌ Конструктор меню (фиксированная структура)
- ❌ CryptoBot (прямая проверка транзакций)
- ❌ Docker

---

## 🏗️ АРХИТЕКТУРА СИСТЕМЫ

```
┌─────────────────────────────────────────────────────────────────┐
│                    АДМИН-ПАНЕЛЬ (React)                         │
│  🌓 Тёмная тема │ 📊 Графики │ 📦 Пакеты │ 📝 Контент │ ⚙️     │
└────────────────────────────┬────────────────────────────────────┘
                             │ REST API
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI)                          │
│                                                                 │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    bot.db (SQLite)                         │ │
│  │  settings │ channels │ packages │ users │ subscriptions    │ │
│  │  payments │ promocodes │ texts │ faq_items │ tasks         │ │
│  └────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        ┌──────────┐  ┌───────────┐  ┌───────────┐
        │ TELEGRAM │  │ BLOCKCHAIN│  │  USERBOT  │
        │   BOT    │  │    API    │  │ (Pyrogram)│
        │ (Aiogram)│  │ TON/TRC20 │  │ Инвайты   │
        │ RU / EN  │  │  Проверка │  │   + Кик   │
        └──────────┘  └───────────┘  └───────────┘
```

---

## 🗄️ СТРУКТУРА БАЗЫ ДАННЫХ

### Файл: `data/bot.db`

---

### Таблица: `settings`
| Поле | Тип | Описание |
|------|-----|----------|
| key | TEXT PK | Ключ настройки |
| value | TEXT | Значение (JSON строка) |
| updated_at | TIMESTAMP | Обновлено |

**Ключи настроек:**
```
support_url           - ссылка на поддержку
default_language      - ru | en
notify_new_users      - true/false (уведомлять о новых юзерах)
notify_payments       - true/false (уведомлять об оплатах)
payment_timeout_min   - таймаут ожидания оплаты (минуты)
promocode_enabled     - показывать кнопку промокода
trial_enabled         - пробный период включён глобально
```

---

### Таблица: `wallets`
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PK | ID |
| network | TEXT | ton / trc20 |
| address | TEXT | Адрес кошелька |
| is_active | BOOLEAN | Активен |
| created_at | TIMESTAMP | Создан |

---

### Таблица: `channels`
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PK | ID |
| channel_id | BIGINT UNIQUE | Telegram ID канала |
| username | TEXT | @username (без @) |
| title | TEXT | Название |
| invite_link | TEXT | Пригласительная ссылка |
| is_active | BOOLEAN | Активен |
| created_at | TIMESTAMP | Создан |

---

### Таблица: `packages`
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PK | ID |
| name_ru | TEXT | Название RU |
| name_en | TEXT | Название EN |
| description_ru | TEXT | Описание RU |
| description_en | TEXT | Описание EN |
| is_active | BOOLEAN | Активен |
| sort_order | INTEGER | Сортировка |
| created_at | TIMESTAMP | Создан |

---

### Таблица: `package_channels` (многие-ко-многим)
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PK | ID |
| package_id | INTEGER FK | Пакет |
| channel_id | INTEGER FK | Канал (channels.id) |

---

### Таблица: `package_options` (варианты срока/цены)
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PK | ID |
| package_id | INTEGER FK | Пакет |
| duration_days | INTEGER | Срок (30/90/365), 0 = навсегда |
| price | REAL | Цена USDT |
| trial_days | INTEGER | Пробный период (0/3/5/7) |
| is_active | BOOLEAN | Активен |
| sort_order | INTEGER | Сортировка |

---

### Таблица: `users`
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PK | ID |
| telegram_id | BIGINT UNIQUE | Telegram ID |
| username | TEXT | @username |
| first_name | TEXT | Имя |
| last_name | TEXT | Фамилия |
| language | TEXT | ru / en |
| trial_used | BOOLEAN | Использовал пробный период |
| is_banned | BOOLEAN | Забанен |
| ban_reason | TEXT | Причина бана |
| created_at | TIMESTAMP | Первый запуск |
| last_activity | TIMESTAMP | Последняя активность |

---

### Таблица: `subscriptions`
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PK | ID |
| user_id | INTEGER FK | Юзер |
| package_id | INTEGER FK | Пакет |
| package_option_id | INTEGER FK | Вариант (срок) |
| is_trial | BOOLEAN | Пробный период |
| starts_at | TIMESTAMP | Начало |
| expires_at | TIMESTAMP | Конец (NULL = навсегда) |
| status | TEXT | active/expired/cancelled/trial |
| auto_kicked | BOOLEAN | Был автокик |
| notified_3days | BOOLEAN | Уведомлён за 3 дня |
| notified_1day | BOOLEAN | Уведомлён за 1 день |
| created_at | TIMESTAMP | Создан |

---

### Таблица: `payments`
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PK | ID |
| user_id | INTEGER FK | Юзер |
| package_option_id | INTEGER FK | Вариант подписки |
| subscription_id | INTEGER FK | Подписка (после оплаты) |
| network | TEXT | ton / trc20 |
| wallet_address | TEXT | Адрес кошелька |
| tx_hash | TEXT | Hash транзакции |
| amount | REAL | Сумма USDT |
| original_amount | REAL | Сумма до скидки |
| promocode_id | INTEGER | Промокод (если был) |
| status | TEXT | pending/checking/paid/failed/expired/manual |
| check_attempts | INTEGER | Попыток проверки |
| paid_at | TIMESTAMP | Оплачен |
| created_at | TIMESTAMP | Создан |

---

### Таблица: `promocodes`
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PK | ID |
| code | TEXT UNIQUE | Код (UPPERCASE) |
| discount_percent | INTEGER | Скидка % (0-100) |
| discount_amount | REAL | Фикс. скидка USDT |
| max_uses | INTEGER | Лимит (NULL = безлимит) |
| used_count | INTEGER | Использований |
| valid_from | TIMESTAMP | Действует с |
| valid_until | TIMESTAMP | Действует до |
| is_active | BOOLEAN | Активен |
| created_at | TIMESTAMP | Создан |

---

### Таблица: `promocode_uses`
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PK | ID |
| promocode_id | INTEGER FK | Промокод |
| user_id | INTEGER FK | Юзер |
| payment_id | INTEGER FK | Платёж |
| used_at | TIMESTAMP | Когда использован |

---

### Таблица: `texts` (контент-менеджер)
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PK | ID |
| key | TEXT UNIQUE | Ключ текста |
| category | TEXT | messages / buttons / notifications |
| text_ru | TEXT | Текст RU |
| text_en | TEXT | Текст EN |
| description | TEXT | Подсказка для админа |
| variables | TEXT | Доступные переменные |
| updated_at | TIMESTAMP | Обновлено |

---

### Таблица: `faq_items`
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PK | ID |
| question_ru | TEXT | Вопрос RU |
| question_en | TEXT | Вопрос EN |
| answer_ru | TEXT | Ответ RU |
| answer_en | TEXT | Ответ EN |
| sort_order | INTEGER | Порядок |
| is_active | BOOLEAN | Активен |
| created_at | TIMESTAMP | Создан |

---

### Таблица: `broadcasts`
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PK | ID |
| message_text | TEXT | Текст |
| message_photo | TEXT | Фото (file_id) |
| buttons_json | TEXT | Кнопки JSON |
| filter_type | TEXT | all/active/inactive |
| filter_language | TEXT | all/ru/en |
| total_users | INTEGER | Всего получателей |
| sent_count | INTEGER | Отправлено |
| failed_count | INTEGER | Ошибок |
| status | TEXT | draft/running/paused/completed/cancelled |
| started_at | TIMESTAMP | Начало |
| completed_at | TIMESTAMP | Конец |
| created_at | TIMESTAMP | Создан |

---

### Таблица: `tasks` (очередь для userbot)
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PK | ID |
| type | TEXT | invite / kick |
| payload | TEXT | JSON с данными |
| status | TEXT | pending/processing/completed/failed |
| attempts | INTEGER | Количество попыток |
| error | TEXT | Текст ошибки |
| created_at | TIMESTAMP | Создан |
| processed_at | TIMESTAMP | Обработан |

---

### Таблица: `admin_logs`
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PK | ID |
| admin_telegram_id | BIGINT | Telegram ID админа |
| action | TEXT | Действие |
| target_user_id | INTEGER | На кого (user.id) |
| details | TEXT | JSON детали |
| created_at | TIMESTAMP | Когда |

---

## 🛠️ ТЕХНОЛОГИЧЕСКИЙ СТЕК

| Компонент | Технология | Версия |
|-----------|------------|--------|
| **Backend API** | FastAPI | 0.109+ |
| **ORM** | SQLAlchemy | 2.0+ |
| **Async SQLite** | aiosqlite | 0.19+ |
| **Telegram Bot** | Aiogram | 3.3+ |
| **Userbot** | Pyrogram | 2.0+ |
| **Blockchain TON** | toncenter API | — |
| **Blockchain TRC20** | trongrid API | — |
| **Frontend** | React + Vite | 18+ |
| **UI** | Tailwind CSS | 3.4+ |
| **Графики** | Recharts | — |
| **HTTP Client** | httpx | 0.26+ |
| **Валидация** | Pydantic | 2.6+ |

---

## 📁 СТРУКТУРА ПРОЕКТА

```
telegram-channel-bot/
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
├── MASTER_PLAN.md
├── CHECKLIST.md
├── CLAUDE_INSTRUCTION.md
│
├── data/                           # Данные (в .gitignore)
│   ├── bot.db                      # База данных
│   └── backups/                    # Бэкапы
│
├── bot/                            # Telegram бот
│   ├── __init__.py
│   ├── run.py                      # Точка входа
│   ├── config.py                   # Настройки
│   ├── loader.py                   # Bot, Dispatcher
│   ├── database.py                 # SQLite подключение
│   │
│   ├── models/                     # SQLAlchemy модели
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── settings.py
│   │   ├── wallet.py
│   │   ├── channel.py
│   │   ├── package.py
│   │   ├── user.py
│   │   ├── subscription.py
│   │   ├── payment.py
│   │   ├── promocode.py
│   │   ├── text.py
│   │   ├── faq.py
│   │   ├── broadcast.py
│   │   ├── task.py
│   │   └── admin_log.py
│   │
│   ├── handlers/                   # Хендлеры
│   │   ├── __init__.py
│   │   ├── start.py
│   │   ├── menu.py
│   │   ├── packages.py
│   │   ├── payment.py
│   │   ├── promocode.py
│   │   ├── subscription.py
│   │   ├── faq.py
│   │   ├── language.py
│   │   └── admin.py
│   │
│   ├── keyboards/
│   │   ├── __init__.py
│   │   └── inline.py
│   │
│   ├── callbacks/
│   │   ├── __init__.py
│   │   ├── package.py
│   │   ├── payment.py
│   │   ├── subscription.py
│   │   ├── faq.py
│   │   ├── language.py
│   │   └── admin.py
│   │
│   ├── middlewares/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── user.py
│   │   ├── i18n.py
│   │   ├── ban.py
│   │   └── rate_limit.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── content.py              # Контент из БД
│   │   ├── blockchain.py           # TON/TRC20 проверка
│   │   ├── subscription.py
│   │   ├── subscription_checker.py
│   │   ├── broadcast.py
│   │   └── notifications.py
│   │
│   └── locales/                    # Дефолтные тексты
│       ├── __init__.py
│       ├── ru.py
│       └── en.py
│
├── userbot/                        # Pyrogram Userbot
│   ├── __init__.py
│   ├── run.py
│   ├── config.py
│   ├── client.py
│   ├── task_processor.py           # Обработка очереди tasks
│   └── actions/
│       ├── __init__.py
│       ├── invite.py
│       └── kick.py
│
├── admin/                          # Админ-панель Backend
│   ├── __init__.py
│   ├── run.py
│   ├── config.py
│   ├── database.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dashboard.py
│   │   ├── packages.py
│   │   ├── channels.py
│   │   ├── users.py
│   │   ├── subscriptions.py
│   │   ├── payments.py
│   │   ├── promocodes.py
│   │   ├── content.py              # texts + faq
│   │   ├── settings.py
│   │   ├── broadcasts.py
│   │   ├── export.py
│   │   └── backup.py
│   │
│   └── schemas/
│       ├── __init__.py
│       ├── package.py
│       ├── channel.py
│       ├── user.py
│       ├── subscription.py
│       ├── payment.py
│       ├── promocode.py
│       ├── content.py
│       ├── settings.py
│       └── broadcast.py
│
├── frontend/                       # React админка
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── index.html
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── index.css
│       │
│       ├── api/
│       ├── context/
│       │   └── ThemeContext.jsx
│       ├── components/
│       │   ├── Layout.jsx
│       │   ├── Sidebar.jsx
│       │   ├── Header.jsx
│       │   ├── ThemeToggle.jsx
│       │   ├── StatsCard.jsx
│       │   ├── Chart.jsx
│       │   ├── DataTable.jsx
│       │   └── Modal.jsx
│       │
│       └── pages/
│           ├── Dashboard.jsx
│           ├── Packages/
│           ├── Users/
│           ├── Payments/
│           ├── Promocodes/
│           ├── Content/
│           ├── Broadcasts/
│           └── Settings/
│
├── scripts/
│   ├── setup_db.py
│   ├── backup_db.py
│   └── generate_session.py
│
└── Windows .bat файлы
    ├── install.bat
    ├── start_bot.bat
    ├── start_admin.bat
    ├── start_userbot.bat
    ├── start_frontend.bat
    ├── start_all.bat
    ├── stop_all.bat
    ├── backup_db.bat
    └── generate_session.bat
```

---

## ⚙️ ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ (.env)

```env
# === TELEGRAM BOT ===
BOT_TOKEN=123456789:AABBCCDDEEFFgghhiijjkkllmmnn

# === USERBOT (Pyrogram) ===
USERBOT_API_ID=12345678
USERBOT_API_HASH=your_api_hash
USERBOT_PHONE=+79001234567
USERBOT_SESSION_STRING=

# === CRYPTO WALLETS ===
TON_WALLET=UQBxxxxxxxxxxxxxxxxxxxxxxxxx
TRC20_WALLET=TXxxxxxxxxxxxxxxxxxxxxxxxxx

# === ADMIN (Telegram IDs через запятую) ===
ADMIN_IDS=123456789,987654321

# === DATABASE ===
DATABASE_PATH=./data/bot.db
BACKUP_DIR=./data/backups

# === SERVER ===
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

# === APP ===
DEBUG=true
SECRET_KEY=your-super-secret-key-change-this
```

---

## 🤖 ФУНКЦИОНАЛ TELEGRAM БОТА

### Фиксированная структура меню:

```
/start
    │
    ▼
┌─────────────────────────────────────┐
│ Выберите язык:                      │
│ [🇷🇺 Русский]  [🇬🇧 English]         │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ Главное меню                        │
│                                     │
│ [📦 Пакеты]                         │
│ [💳 Мои подписки]                   │
│ [🎁 Промокод]      ← если включён   │
│ [❓ FAQ]                            │
│ [🌐 Язык]                           │
│ [💬 Поддержка]                      │
└─────────────────────────────────────┘
```

### Флоу покупки:

```
[📦 Пакеты] → Выбор пакета → Выбор срока → Выбор сети (TON/TRC20)
    → Показ адреса → Юзер переводит → Отправляет hash → Проверка
    → Успех → Invite в каналы → Ссылки юзеру
```

### "Мои подписки":

```
┌─────────────────────────────────────┐
│ 💳 Ваши подписки:                   │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ 📦 Премиум                      │ │
│ │ ✅ Активна до: 15.02.2025       │ │
│ │                                 │ │
│ │ [🔗 Ссылки на каналы]           │ │
│ │ [🔄 Продлить]                   │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

### Команды:
| Команда | Описание |
|---------|----------|
| `/start` | Запуск, выбор языка, меню |
| `/menu` | Главное меню |
| `/language` | Сменить язык |
| `/admin` | Админ-панель (только для админов) |
| `/stats` | Быстрая статистика (для админов) |

---

## 🖥️ ФУНКЦИОНАЛ АДМИН-ПАНЕЛИ

### Разделы:

| Раздел | Что там |
|--------|---------|
| **📊 Dashboard** | Статистика, графики дохода |
| **📦 Пакеты** | Конструктор: каналы + варианты сроков |
| **👥 Пользователи** | Список, бан, выдача доступа |
| **💳 Платежи** | История, ручное подтверждение |
| **🎟️ Промокоды** | CRUD промокодов |
| **📝 Контент** | Все тексты + FAQ |
| **⚙️ Настройки** | On/off, кошельки |
| **📨 Рассылки** | Создание и отправка |

### Конструктор пакетов:

```
┌─────────────────────────────────────────────────────────────┐
│ 📦 Премиум                                       [✏️][🗑️]  │
├─────────────────────────────────────────────────────────────┤
│ 📺 Каналы:                                                  │
│ • @signals — Трейдинг сигналы                              │
│ • @vip_signals — VIP сигналы                               │
│                                    [+ Добавить канал]       │
├─────────────────────────────────────────────────────────────┤
│ 💰 Варианты подписки:                                       │
│ │ 30 дней   │ $25   │ 🎁 Trial: 7 дней │ [✏️] [🗑️]       │
│ │ 90 дней   │ $60   │ —                │ [✏️] [🗑️]       │
│ │ 365 дней  │ $200  │ —                │ [✏️] [🗑️]       │
│                              [+ Добавить вариант]           │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 ЭТАПЫ РАЗРАБОТКИ (6 ЧАТОВ)

### ЧАТ 1: Структура + БД
- Структура папок
- SQLAlchemy модели (все таблицы)
- Скрипт инициализации БД + дефолтные тексты
- Базовый FastAPI с health check
- `install.bat`, `start_admin.bat`

### ЧАТ 2: Бот — ядро
- Aiogram 3 бот
- Middleware: БД, юзер, бан, язык, rate limit
- /start → язык → меню
- Список пакетов → детали → выбор срока
- Контент из БД (таблица texts)
- `start_bot.bat`

### ЧАТ 3: Оплата + Userbot
- Выбор сети (TON/TRC20)
- Показ адреса кошелька
- Приём hash от юзера
- Проверка транзакции через API
- Pyrogram userbot: invite в каналы
- Таблица tasks для очереди
- `start_userbot.bat`, `generate_session.bat`

### ЧАТ 4: Подписки + фичи
- "Мои подписки" со ссылками на каналы
- Кнопка "Продлить"
- Промокоды
- FAQ
- Пробный период (3/5/7 дней)
- Уведомления за 3 дня / 1 день
- Автокик при истечении
- /admin команды в боте

### ЧАТ 5: Backend API
- Dashboard: статистика, графики
- CRUD: пакеты, каналы, юзеры, платежи, промокоды
- Контент: тексты, FAQ
- Настройки: кошельки, переключатели
- Рассылки
- Экспорт CSV, бэкапы

### ЧАТ 6: Frontend
- React + Vite + Tailwind
- Тёмная тема
- Dashboard с графиками
- Конструктор пакетов
- Все страницы CRUD
- Редактор контента
- `start_frontend.bat`, `start_all.bat`

---

## 🚀 БЫСТРЫЙ СТАРТ (Windows)

```cmd
:: 1. Клонировать репозиторий
git clone https://github.com/ironsan2kk-pixel/TGconst.git
cd TGconst

:: 2. Установка
install.bat

:: 3. Настроить .env
:: Открыть .env и заполнить BOT_TOKEN, ADMIN_IDS, кошельки

:: 4. Запустить всё
start_all.bat
```

---

**Готов к работе. Жду "Чат 1"!**
