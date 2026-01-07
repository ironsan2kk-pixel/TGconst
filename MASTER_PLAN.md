# 🔧 МАСТЕР-ПЛАН: Telegram-бот продажи доступа к каналам

**Версия:** 4.0  
**Дата:** Январь 2025  
**Платформа:** Windows Server  
**Архитектура:** Один бот, SQLite, без Docker

---

## 📌 ОБЩЕЕ ОПИСАНИЕ

### Что это?
Telegram-бот для продажи доступа к приватным каналам через криптовалюту (TON/TRC20 USDT).

### Ключевые особенности:
- **Один бот** — фиксированный шаблон, быстрый деплой
- **Пакеты каналов** — один пакет = несколько каналов + варианты сроков (30/90/365 дней)
- **Два языка** — русский и английский с переключением
- **Пробный период** — 3/5/7 дней опционально для каждого варианта
- **Оплата криптой** — TON и TRC20 (USDT), проверка по hash транзакции
- **Тёмная тема** — в админке с переключателем
- **Контент-менеджер** — все тексты редактируются в админке
- **Напоминания** — о продлении подписки (за 3 дня, за 1 день)
- **Ручное подтверждение** — админ может подтвердить оплату без крипты
- **Уведомления админу** — о новых юзерах и покупках прямо в Telegram

### НЕ включено:
- ❌ Конструктор меню (фиксированная структура)
- ❌ CryptoBot (прямая проверка транзакций)
- ❌ Docker

---

## 🏗️ АРХИТЕКТУРА СИСТЕМЫ

```
┌─────────────────────────────────────────────────────────────────┐
│                    АДМИН-ПАНЕЛЬ (React)                         │
│  🌓 Тёмная тема │ 📦 Пакеты │ 📝 Контент │ 👥 Юзеры │ 📨 Рассылки│
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
notify_new_users      - true/false
notify_payments       - true/false
payment_timeout_min   - таймаут ожидания оплаты (минуты)
promocode_enabled     - показывать кнопку промокода
trial_enabled         - пробный период включён глобально
ton_wallet            - адрес TON кошелька
trc20_wallet          - адрес TRC20 кошелька
```

---

### Таблица: `channels`
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PK | ID |
| channel_id | BIGINT UNIQUE | Telegram ID канала |
| username | TEXT | @username (без @) |
| title | TEXT | Название |
| description | TEXT | Описание |
| invite_link | TEXT | Пригласительная ссылка |
| is_active | BOOLEAN | Активен |
| is_deleted | BOOLEAN | Удалён (soft delete) |
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
| is_deleted | BOOLEAN | Удалён (soft delete) |
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

### Таблица: `package_options` (варианты подписки)
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PK | ID |
| package_id | INTEGER FK | Пакет |
| duration_days | INTEGER | Срок (дни): 30, 90, 365, 0 = навсегда |
| price | REAL | Цена USDT |
| trial_days | INTEGER | Пробный период: 0, 3, 5, 7 |
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
| package_option_id | INTEGER FK | Вариант подписки |
| status | TEXT | active/expired/cancelled/trial |
| starts_at | TIMESTAMP | Начало |
| expires_at | TIMESTAMP | Конец (NULL = навсегда) |
| auto_kicked | BOOLEAN | Был автокик |
| notified_3days | BOOLEAN | Уведомлён за 3 дня |
| notified_1day | BOOLEAN | Уведомлён за 1 день |
| granted_by | BIGINT | Кто выдал (admin telegram_id) |
| created_at | TIMESTAMP | Создан |

---

### Таблица: `payments`
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PK | ID |
| user_id | INTEGER FK | Юзер |
| package_option_id | INTEGER FK | Вариант подписки |
| subscription_id | INTEGER FK | Подписка |
| network | TEXT | ton / trc20 |
| wallet_address | TEXT | Адрес кошелька |
| tx_hash | TEXT UNIQUE | Hash транзакции |
| amount | REAL | Сумма USDT |
| original_amount | REAL | Сумма до скидки |
| promocode_id | INTEGER | Промокод (если был) |
| status | TEXT | pending/checking/confirmed/failed/manual |
| payment_method | TEXT | crypto / manual |
| confirmed_by | BIGINT | Кто подтвердил (для manual) |
| check_attempts | INTEGER | Количество проверок |
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

**Ключи текстов:**
```
# messages
welcome              - Приветствие
language_prompt      - Выберите язык
packages_list        - Список пакетов
package_details      - Детали пакета
payment_prompt       - Инструкция по оплате
payment_success      - Оплата прошла
payment_failed       - Оплата не найдена
subscription_active  - Подписка активирована
subscription_expiring_3d - Истекает через 3 дня
subscription_expiring_1d - Истекает завтра
subscription_expired - Подписка истекла
trial_started        - Пробный период начат
promocode_applied    - Промокод применён
promocode_invalid    - Неверный промокод

# buttons
btn_packages         - Пакеты
btn_subscriptions    - Мои подписки
btn_promocode        - Промокод
btn_faq              - FAQ
btn_language         - Язык
btn_support          - Поддержка
btn_back             - Назад
btn_pay              - Оплатить
btn_cancel           - Отмена
btn_renew            - Продлить
btn_links            - Ссылки на каналы
```

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

### Таблица: `tasks` (очередь для userbot)
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PK | ID |
| type | TEXT | invite / kick |
| user_telegram_id | BIGINT | Telegram ID юзера |
| channel_id | BIGINT | Telegram ID канала |
| payload | TEXT | JSON дополнительные данные |
| status | TEXT | pending/processing/completed/failed |
| attempts | INTEGER | Количество попыток |
| error | TEXT | Текст ошибки |
| created_at | TIMESTAMP | Создан |
| processed_at | TIMESTAMP | Обработан |

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

## 🤖 TELEGRAM БОТ — ФИКСИРОВАННАЯ СТРУКТУРА

### Флоу пользователя:

```
/start
    │
    ▼
[Выбор языка: 🇷🇺 / 🇬🇧]
    │
    ▼
┌─────────────────────────┐
│     ГЛАВНОЕ МЕНЮ        │
├─────────────────────────┤
│ [📦 Пакеты]             │
│ [💳 Мои подписки]       │
│ [🎁 Промокод]  *        │
│ [❓ FAQ]                │
│ [🌐 Язык]               │
│ [💬 Поддержка]          │
└─────────────────────────┘
    * если включён в настройках
```

### Флоу покупки:

```
[📦 Пакеты] → Список пакетов → Детали пакета
    │
    ▼
Выбор срока: [30 дней $25] [90 дней $60] [1 год $200]
    │
    ▼
Выбор сети: [TON] [TRC20]
    │
    ▼
Показ адреса кошелька + инструкция
    │
    ▼
Юзер отправляет hash транзакции (текстом)
    │
    ▼
Проверка через API → Успех → Создание подписки → Invite в каналы
```

### "Мои подписки":

```
[💳 Мои подписки]
    │
    ▼
┌─────────────────────────────────┐
│ 📦 Премиум                      │
│ ✅ Активна до: 15.02.2025       │
│ Осталось: 24 дня                │
│                                 │
│ [🔗 Ссылки на каналы]           │
│ [🔄 Продлить]                   │
└─────────────────────────────────┘
```

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
│   │   ├── channel.py
│   │   ├── package.py
│   │   ├── user.py
│   │   ├── subscription.py
│   │   ├── payment.py
│   │   ├── promocode.py
│   │   ├── text.py
│   │   ├── faq.py
│   │   ├── task.py
│   │   ├── broadcast.py
│   │   └── admin_log.py
│   │
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── start.py
│   │   ├── menu.py
│   │   ├── packages.py
│   │   ├── payment.py
│   │   ├── subscriptions.py
│   │   ├── promocode.py
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
│   │   ├── content.py              # Работа с таблицей texts
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
│   │   ├── broadcasts.py
│   │   ├── settings.py
│   │   ├── export.py
│   │   └── backup.py
│   │
│   └── schemas/
│       ├── __init__.py
│       └── ... (Pydantic schemas)
│
├── frontend/                       # React админка
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── pages/
│       │   ├── Dashboard.jsx
│       │   ├── Packages/           # Конструктор пакетов
│       │   ├── Users/
│       │   ├── Payments/
│       │   ├── Promocodes/
│       │   ├── Content/            # Тексты + FAQ
│       │   ├── Broadcasts/
│       │   └── Settings/
│       └── components/
│
├── scripts/
│   ├── setup_db.py
│   ├── backup_db.py
│   └── generate_session.py
│
└── Windows .bat файлы
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

# === ADMIN (Telegram IDs через запятую) ===
ADMIN_IDS=123456789,987654321

# === CRYPTO WALLETS ===
TON_WALLET=UQBxxxxxxxxxxxxxxxxxxxxxx
TRC20_WALLET=TXxxxxxxxxxxxxxxxxxxxxxx

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

## 📊 ЭТАПЫ РАЗРАБОТКИ (6 ЧАТОВ)

### ЧАТ 1: Структура и база данных
- Структура папок
- requirements.txt, .env.example, .gitignore
- SQLAlchemy модели (все таблицы)
- Скрипт инициализации БД + дефолтные тексты
- Базовый FastAPI с health check
- Windows .bat файлы (install, start_admin)

### ЧАТ 2: Telegram бот — Ядро
- Aiogram 3 бот
- Контент из БД (таблица texts)
- Middleware: БД, юзер, бан, язык, rate limit
- /start с выбором языка
- Главное меню
- Список пакетов → детали → выбор срока
- Уведомления админам о новых юзерах

### ЧАТ 3: Оплата + Userbot
- Выбор сети (TON/TRC20)
- Показ адреса кошелька
- Приём hash от юзера
- Проверка транзакции через API
- Pyrogram userbot: invite/kick
- Таблица tasks для очереди
- Полный цикл: оплата → доступ

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
- Настройки
- Рассылки
- Экспорт CSV, бэкапы

### ЧАТ 6: Frontend
- React + Vite + Tailwind
- Тёмная тема
- Dashboard с графиками
- Конструктор пакетов
- Редактор контента
- Все страницы

---

## 🚀 БЫСТРЫЙ СТАРТ (Windows)

```cmd
:: 1. Клонировать репозиторий
git clone https://github.com/your-repo/telegram-channel-bot.git
cd telegram-channel-bot

:: 2. Установка
install.bat

:: 3. Настроить .env
:: Заполнить BOT_TOKEN, ADMIN_IDS, кошельки

:: 4. Запустить всё
start_all.bat
```

---

**Готов к работе. Жду "Чат 1"!**
