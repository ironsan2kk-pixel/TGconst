# 🔧 МАСТЕР-ПЛАН: Telegram-бот продажи доступа к каналам

**Версия:** 4.0  
**Дата:** Январь 2025  
**Платформа:** Windows Server  
**Архитектура:** Один бот, SQLite, два языка (RU/EN)

---

## 📌 ОБЩЕЕ ОПИСАНИЕ

### Что это?
Telegram-бот для продажи доступа к приватным каналам через криптовалюту (CryptoBot/USDT) с полной веб-админкой.

### Ключевые особенности:
- **Один бот** — простая архитектура
- **Пакеты каналов** — один тариф = доступ к нескольким каналам
- **Два языка** — русский и английский с переключением
- **Пробный период** — опционально для каждого тарифа
- **Deep Links** — прямые ссылки на тарифы
- **Кастомные кнопки** — добавляй свои кнопки в меню
- **Уведомления админу** — о новых юзерах и покупках
- **Ручное подтверждение** — админ может подтвердить оплату
- **Напоминания** — о продлении подписки со скидкой
- **Полная админка** — с тёмной темой и графиками аналитики

### Платформа:
- **Windows Server** — все скрипты .bat с UTF-8
- **Python 3.11+** — виртуальное окружение
- **Node.js 18+** — для React админки

---

## 🏗️ АРХИТЕКТУРА СИСТЕМЫ

\`\`\`
┌─────────────────────────────────────────────────────────────────┐
│                 АДМИН-ПАНЕЛЬ (React + Tailwind)                 │
│         Тёмная тема │ Графики │ Dashboard │ CRUD                │
└────────────────────────────┬────────────────────────────────────┘
                             │ REST API
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI)                          │
│                                                                 │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    bot.db (SQLite)                         │ │
│  │  settings │ channels │ tariffs │ tariff_channels           │ │
│  │  users │ subscriptions │ payments │ promocodes             │ │
│  │  broadcasts │ custom_buttons │ admin_logs │ stats_daily    │ │
│  └────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        ┌──────────┐  ┌───────────┐  ┌───────────┐
        │ TELEGRAM │  │ CRYPTOBOT │  │  USERBOT  │
        │   BOT    │  │    API    │  │ (Pyrogram)│
        │ (Aiogram)│  │  Платежи  │  │ Инвайты   │
        │ RU / EN  │  │   USDT    │  │   Кики    │
        └──────────┘  └───────────┘  └───────────┘
\`\`\`

---

## 🗄️ СТРУКТУРА БАЗЫ ДАННЫХ

### Файл: data/bot.db

### Таблица: settings
| Поле | Тип | Описание |
|------|-----|----------|
| key | TEXT PK | Ключ настройки |
| value | TEXT | Значение (JSON) |
| updated_at | TIMESTAMP | Обновлено |

Ключи: bot_token, bot_username, cryptobot_token, admin_ids, admin_password_hash, welcome_message_ru, welcome_message_en, support_url, default_language, reminder_days, reminder_discount

### Таблица: channels
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PK | ID |
| channel_id | BIGINT UNIQUE | Telegram ID канала |
| username | TEXT | @username |
| title | TEXT | Название |
| description | TEXT | Описание |
| invite_link | TEXT | Ссылка |
| is_active | INTEGER | 0/1 |
| sort_order | INTEGER | Сортировка |
| created_at | TIMESTAMP | Создан |

### Таблица: tariffs
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PK | ID |
| name_ru | TEXT | Название RU |
| name_en | TEXT | Название EN |
| description_ru | TEXT | Описание RU |
| description_en | TEXT | Описание EN |
| price | REAL | Цена USDT |
| duration_days | INTEGER | Срок (0=навсегда) |
| trial_days | INTEGER | Пробный период |
| is_active | INTEGER | 0/1 |
| sort_order | INTEGER | Сортировка |
| created_at | TIMESTAMP | Создан |

### Таблица: tariff_channels
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PK | ID |
| tariff_id | INTEGER FK | Тариф |
| channel_id | INTEGER FK | Канал |

### Таблица: users
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PK | ID |
| telegram_id | BIGINT UNIQUE | Telegram ID |
| username | TEXT | @username |
| first_name | TEXT | Имя |
| last_name | TEXT | Фамилия |
| language | TEXT | ru/en |
| is_banned | INTEGER | 0/1 |
| ban_reason | TEXT | Причина |
| source | TEXT | utm/deep link |
| created_at | TIMESTAMP | Создан |
| last_activity | TIMESTAMP | Активность |

### Таблица: subscriptions
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PK | ID |
| user_id | INTEGER FK | Юзер |
| tariff_id | INTEGER FK | Тариф |
| is_trial | INTEGER | 0/1 |
| starts_at | TIMESTAMP | Начало |
| expires_at | TIMESTAMP | Конец |
| is_active | INTEGER | 0/1 |
| auto_kicked | INTEGER | 0/1 |
| reminded_at | TIMESTAMP | Напоминание |
| granted_by | TEXT | Кто выдал |
| created_at | TIMESTAMP | Создан |

### Таблица: payments
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PK | ID |
| user_id | INTEGER FK | Юзер |
| tariff_id | INTEGER FK | Тариф |
| subscription_id | INTEGER FK | Подписка |
| invoice_id | TEXT | CryptoBot ID |
| amount | REAL | Сумма |
| original_amount | REAL | До скидки |
| promocode_id | INTEGER | Промокод |
| status | TEXT | pending/paid/expired/manual |
| confirmed_by | BIGINT | Подтвердил |
| paid_at | TIMESTAMP | Оплачен |
| created_at | TIMESTAMP | Создан |

### Таблица: promocodes
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PK | ID |
| code | TEXT UNIQUE | Код |
| discount_percent | INTEGER | Скидка % |
| discount_amount | REAL | Фикс скидка |
| max_uses | INTEGER | Лимит |
| used_count | INTEGER | Использований |
| valid_from | TIMESTAMP | С |
| valid_until | TIMESTAMP | До |
| tariff_id | INTEGER | Для тарифа |
| is_active | INTEGER | 0/1 |
| created_at | TIMESTAMP | Создан |

### Таблица: promocode_uses
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PK | ID |
| promocode_id | INTEGER FK | Промокод |
| user_id | INTEGER FK | Юзер |
| payment_id | INTEGER FK | Платёж |
| used_at | TIMESTAMP | Когда |

### Таблица: broadcasts
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PK | ID |
| message_text | TEXT | Текст |
| message_photo | TEXT | Фото |
| buttons_json | TEXT | Кнопки |
| filter_type | TEXT | all/active/inactive |
| filter_language | TEXT | all/ru/en |
| total_users | INTEGER | Всего |
| sent_count | INTEGER | Отправлено |
| failed_count | INTEGER | Ошибок |
| status | TEXT | draft/running/completed |
| started_at | TIMESTAMP | Начало |
| completed_at | TIMESTAMP | Конец |
| created_at | TIMESTAMP | Создан |

### Таблица: custom_buttons
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PK | ID |
| text_ru | TEXT | Текст RU |
| text_en | TEXT | Текст EN |
| type | TEXT | url/text |
| value | TEXT | Значение |
| sort_order | INTEGER | Сортировка |
| is_active | INTEGER | 0/1 |
| created_at | TIMESTAMP | Создан |

### Таблица: admin_logs
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PK | ID |
| admin_id | BIGINT | Админ ID |
| action | TEXT | Действие |
| target_user_id | BIGINT | Цель |
| details | TEXT | Детали JSON |
| created_at | TIMESTAMP | Когда |

### Таблица: stats_daily
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PK | ID |
| date | DATE UNIQUE | Дата |
| new_users | INTEGER | Новых |
| active_users | INTEGER | Активных |
| new_subscriptions | INTEGER | Подписок |
| expired_subscriptions | INTEGER | Истекло |
| revenue | REAL | Доход |
| created_at | TIMESTAMP | Создан |

---

## 🛠️ ТЕХНОЛОГИЧЕСКИЙ СТЕК

| Компонент | Технология |
|-----------|------------|
| Backend API | FastAPI 0.109+ |
| ORM | SQLAlchemy 2.0+ |
| Async SQLite | aiosqlite 0.19+ |
| Telegram Bot | Aiogram 3.3+ |
| Userbot | Pyrogram 2.0+ |
| Крипто-оплата | CryptoBot API |
| Frontend | React 18+ Vite |
| UI | Tailwind CSS 3.4+ |
| Графики | Recharts 2.10+ |
| HTTP | httpx 0.26+ |
| Auth | python-jose, passlib |
| Платформа | Windows Server |

---

## 📁 СТРУКТУРА ПРОЕКТА

\`\`\`
telegram-channel-bot/
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
├── MASTER_PLAN.md
├── CHECKLIST.md
├── CLAUDE_INSTRUCTION.md
├── data/
│   ├── bot.db
│   ├── backups/
│   └── logs/
├── bot/
│   ├── run.py
│   ├── loader.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   ├── handlers/
│   ├── keyboards/
│   ├── callbacks/
│   ├── middlewares/
│   ├── services/
│   ├── utils/
│   └── locales/
├── userbot/
│   ├── run.py
│   ├── config.py
│   ├── client.py
│   └── actions/
├── admin/
│   ├── run.py
│   ├── config.py
│   ├── database.py
│   ├── api/
│   ├── schemas/
│   └── utils/
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── src/
│       ├── App.jsx
│       ├── api/
│       ├── context/
│       ├── components/
│       ├── pages/
│       └── hooks/
└── scripts/
    ├── install.bat
    ├── start_bot.bat
    ├── start_admin.bat
    ├── start_userbot.bat
    ├── start_frontend.bat
    ├── start_all.bat
    ├── stop_all.bat
    ├── backup_db.bat
    ├── setup_db.py
    └── generate_session.py
\`\`\`

---

## 📊 ЧАТЫ РАЗРАБОТКИ (8 чатов)

| # | Чат | Что делаем |
|---|-----|------------|
| 1 | Структура и БД | Папки, модели, инициализация |
| 2 | Бот — Ядро | /start, меню, тарифы, i18n, deep links |
| 3 | CryptoBot | Оплата, webhook, подписки |
| 4 | Userbot | Pyrogram, инвайты в каналы |
| 5 | Подписки | Проверка, напоминания, автокик |
| 6 | Фичи бота | Промокоды, /admin, ручное подтверждение |
| 7 | Рассылки | Создание, фильтры, отправка |
| 8 | Админка | API + React с темой и графиками |

---

## 🚀 БЫСТРЫЙ СТАРТ

\`\`\`cmd
:: 1. Клонировать
git clone https://github.com/ironsan2kk-pixel/TGconst.git
cd TGconst

:: 2. Установка
scripts\install.bat

:: 3. Настройка
notepad .env

:: 4. БД
python scripts\setup_db.py

:: 5. Запуск
scripts\start_all.bat
\`\`\`

**Жду "Чат 1"!**
