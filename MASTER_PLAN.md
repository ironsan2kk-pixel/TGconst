# 🔧 МАСТЕР-ПЛАН: Конструктор Telegram-ботов

**Версия:** 2.0  
**Дата:** Январь 2025  
**Особенности:** Без Docker, SQLite для каждого бота отдельно

---

## 📌 ОБЩЕЕ ОПИСАНИЕ

### Что это?
Веб-приложение (админ-панель) для создания Telegram-ботов, которые продают доступ к приватным каналам через криптовалюту (CryptoBot).

### Ключевые особенности:
- **Без Docker** — чистый Python, запуск через systemd/supervisor
- **SQLite для каждого бота** — изолированные базы данных
- **Одна главная SQLite** — для админки (список ботов, настройки)

### Основной функционал:
- Создание ботов через админку (без кода)
- Приём оплаты через CryptoBot (@CryptoPay)
- Автоматическое добавление в канал после оплаты (Userbot)
- Автоматическая проверка подписки и кик по истечении
- Промокоды со скидками
- Массовые рассылки по пользователям

---

## 🏗️ АРХИТЕКТУРА СИСТЕМЫ

```
┌─────────────────────────────────────────────────────────────────┐
│                      АДМИН-ПАНЕЛЬ (React)                       │
│  Дашборд │ Боты │ Каналы │ Тарифы │ Промокоды │ Рассылки        │
└────────────────────────────┬────────────────────────────────────┘
                             │ REST API
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI)                          │
│                                                                 │
│  ┌────────────────────┐    ┌────────────────────────────────┐  │
│  │   main.db (SQLite) │    │      ОРКЕСТРАТОР БОТОВ         │  │
│  │   - admins         │    │   Запуск/Остановка процессов   │  │
│  │   - bots (список)  │    │   (subprocess / supervisor)    │  │
│  │   - settings       │    └────────────────────────────────┘  │
│  └────────────────────┘                                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
   ┌───────────┐       ┌───────────┐       ┌───────────┐
   │  Bot #1   │       │  Bot #2   │       │  Bot #N   │
   │ (Aiogram) │       │ (Aiogram) │       │ (Aiogram) │
   │           │       │           │       │           │
   │ bot_1.db  │       │ bot_2.db  │       │ bot_N.db  │
   │ - users   │       │ - users   │       │ - users   │
   │ - subs    │       │ - subs    │       │ - subs    │
   │ - payments│       │ - payments│       │ - payments│
   └─────┬─────┘       └─────┬─────┘       └─────┬─────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             ▼
                    ┌───────────────┐
                    │    USERBOT    │
                    │  (Pyrogram)   │
                    │ Добавление/Кик│
                    └───────────────┘
```

---

## 🗄️ СТРУКТУРА БАЗ ДАННЫХ

### 1. Главная база: `data/main.db`

**Таблица: admins**
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PK | ID |
| username | TEXT | Логин |
| password_hash | TEXT | Хеш пароля |
| created_at | TIMESTAMP | Дата создания |

**Таблица: bots**
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PK | ID бота |
| uuid | TEXT | UUID для путей |
| name | TEXT | Название |
| bot_token | TEXT | Токен Telegram |
| cryptobot_token | TEXT | Токен CryptoBot |
| welcome_message | TEXT | Приветствие |
| support_url | TEXT | Ссылка поддержки |
| is_active | INTEGER | 0/1 |
| process_pid | INTEGER | PID процесса |
| created_at | TIMESTAMP | Создан |
| updated_at | TIMESTAMP | Обновлён |

**Таблица: userbot_config**
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PK | ID |
| api_id | INTEGER | Telegram API ID |
| api_hash | TEXT | Telegram API Hash |
| phone | TEXT | Номер телефона |
| session_string | TEXT | Сессия Pyrogram |

---

### 2. База каждого бота: `data/bots/{uuid}/bot.db`

**Таблица: channels**
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PK | ID |
| channel_id | INTEGER | Telegram ID канала |
| channel_username | TEXT | @username |
| title | TEXT | Название |
| is_active | INTEGER | 0/1 |
| created_at | TIMESTAMP | Создан |

**Таблица: tariffs**
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PK | ID |
| channel_id | INTEGER FK | Канал |
| name | TEXT | Название |
| price | REAL | Цена USD |
| duration_days | INTEGER | Срок (дни) |
| is_active | INTEGER | 0/1 |
| sort_order | INTEGER | Сортировка |

**Таблица: users**
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PK | ID |
| telegram_id | INTEGER | Telegram ID |
| username | TEXT | @username |
| first_name | TEXT | Имя |
| last_name | TEXT | Фамилия |
| is_blocked | INTEGER | Заблокировал бота |
| created_at | TIMESTAMP | Первый запуск |
| last_activity | TIMESTAMP | Последняя активность |

**Таблица: subscriptions**
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PK | ID |
| user_id | INTEGER FK | Юзер |
| channel_id | INTEGER FK | Канал |
| tariff_id | INTEGER FK | Тариф |
| starts_at | TIMESTAMP | Начало |
| expires_at | TIMESTAMP | Конец |
| is_active | INTEGER | 0/1 |
| auto_kicked | INTEGER | Был кик |

**Таблица: payments**
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PK | ID |
| user_id | INTEGER FK | Юзер |
| subscription_id | INTEGER | Подписка |
| invoice_id | TEXT | ID инвойса CryptoBot |
| amount | REAL | Сумма |
| currency | TEXT | Валюта |
| status | TEXT | pending/paid/expired |
| promocode_id | INTEGER | Промокод |
| discount_amount | REAL | Скидка |
| paid_at | TIMESTAMP | Оплачен |
| created_at | TIMESTAMP | Создан |

**Таблица: promocodes**
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PK | ID |
| code | TEXT | Код |
| discount_percent | INTEGER | Скидка % |
| discount_amount | REAL | Фикс. скидка |
| max_uses | INTEGER | Лимит (null=безлимит) |
| used_count | INTEGER | Использований |
| valid_from | TIMESTAMP | Действует с |
| valid_until | TIMESTAMP | Действует до |
| is_active | INTEGER | 0/1 |

**Таблица: broadcasts**
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PK | ID |
| message_text | TEXT | Текст |
| message_photo | TEXT | Фото |
| total_users | INTEGER | Всего |
| sent_count | INTEGER | Отправлено |
| failed_count | INTEGER | Ошибок |
| status | TEXT | pending/running/completed |
| started_at | TIMESTAMP | Начало |
| completed_at | TIMESTAMP | Конец |

---

## 🛠️ ТЕХНОЛОГИЧЕСКИЙ СТЕК

| Компонент | Технология | Зачем |
|-----------|------------|-------|
| **Backend** | Python 3.11+ FastAPI | REST API |
| **ORM** | SQLAlchemy 2.0 + aiosqlite | Async SQLite |
| **База данных** | SQLite | Отдельная на каждого бота |
| **Telegram Bot** | Aiogram 3.3+ | Bot API |
| **Userbot** | Pyrogram 2.0+ | Добавление в каналы |
| **Крипто-оплата** | CryptoBot API | Платежи |
| **Frontend** | React + Vite | Админка |
| **UI** | Tailwind CSS | Стили |
| **Процессы** | subprocess + supervisor | Управление ботами |
| **Сервер** | uvicorn + nginx | Продакшен |

---

## 📁 СТРУКТУРА ПРОЕКТА

```
telegram-bot-constructor/
├── requirements.txt
├── .env.example
├── README.md
├── MASTER_PLAN.md
├── CHECKLIST.md
│
├── data/                           # ВСЕ ДАННЫЕ
│   ├── main.db                     # Главная база (боты, админы)
│   └── bots/                       # Папки ботов
│       ├── {uuid_1}/
│       │   ├── bot.db              # База бота
│       │   └── logs/               # Логи
│       ├── {uuid_2}/
│       │   ├── bot.db
│       │   └── logs/
│       └── ...
│
├── backend/
│   ├── run.py                      # Запуск FastAPI
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI приложение
│   │   ├── config.py               # Настройки
│   │   ├── database.py             # SQLite подключение
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── main_db.py          # Модели главной БД
│   │   │   └── bot_db.py           # Модели БД бота
│   │   │
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── bot.py
│   │   │   ├── channel.py
│   │   │   ├── tariff.py
│   │   │   ├── user.py
│   │   │   ├── promocode.py
│   │   │   └── broadcast.py
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── deps.py
│   │   │   ├── auth.py
│   │   │   ├── bots.py
│   │   │   ├── channels.py
│   │   │   ├── tariffs.py
│   │   │   ├── promocodes.py
│   │   │   ├── broadcasts.py
│   │   │   ├── users.py
│   │   │   └── webhooks.py
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── bot_manager.py      # Оркестратор
│   │   │   ├── cryptobot.py        # CryptoBot API
│   │   │   └── subscription_checker.py
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── security.py
│   │
│   └── bot_template/
│       ├── __init__.py
│       ├── run.py                  # Точка входа бота
│       ├── loader.py
│       ├── config.py
│       ├── database.py             # Подключение к bot.db
│       │
│       ├── handlers/
│       │   ├── __init__.py
│       │   ├── start.py
│       │   ├── menu.py
│       │   ├── channels.py
│       │   ├── tariffs.py
│       │   ├── payment.py
│       │   ├── promocode.py
│       │   ├── subscription.py
│       │   └── support.py
│       │
│       ├── keyboards/
│       │   ├── __init__.py
│       │   ├── inline.py
│       │   └── reply.py
│       │
│       └── callbacks/
│           ├── __init__.py
│           └── payment.py
│
├── userbot/
│   ├── run.py
│   ├── config.py
│   ├── client.py                   # Pyrogram client
│   └── actions/
│       ├── __init__.py
│       ├── invite.py
│       └── kick.py
│
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── index.html
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── api/
│       ├── components/
│       ├── pages/
│       ├── context/
│       └── hooks/
│
└── scripts/
    ├── install.sh                  # Установка зависимостей
    ├── create_admin.py             # Создание админа
    ├── start_backend.sh            # Запуск backend
    ├── start_userbot.sh            # Запуск userbot
    └── supervisor/
        ├── backend.conf
        └── userbot.conf
```

---

## ⚙️ ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ (.env)

```env
# === APP ===
DEBUG=true
SECRET_KEY=your-super-secret-key-change-this

# === PATHS ===
DATA_DIR=./data
MAIN_DB_PATH=./data/main.db

# === JWT ===
JWT_SECRET_KEY=your-jwt-secret
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# === ADMIN (первый запуск) ===
ADMIN_USERNAME=admin
ADMIN_PASSWORD=changeme123

# === USERBOT (Pyrogram) ===
USERBOT_API_ID=12345678
USERBOT_API_HASH=your_api_hash
USERBOT_PHONE=+79001234567
USERBOT_SESSION_STRING=

# === SERVER ===
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
FRONTEND_URL=http://localhost:3000
WEBHOOK_BASE_URL=https://your-domain.com
```

---

## 📊 ЭТАПЫ РАЗРАБОТКИ (15 этапов)

### ЭТАП 1: Структура проекта
- Создать все папки
- requirements.txt
- .env.example
- Базовый FastAPI с health check
- Подключение к SQLite

**Результат:** `python backend/run.py` запускает API

---

### ЭТАП 2: База данных — Модели
- Модели для main.db (admins, bots, userbot_config)
- Модели для bot.db (channels, tariffs, users, subscriptions, payments, promocodes, broadcasts)
- Функции создания таблиц
- Seed-скрипт для первого админа

**Результат:** Таблицы создаются автоматически

---

### ЭТАП 3: Backend API — Auth
- JWT авторизация
- POST /api/auth/login
- GET /api/auth/me
- Middleware проверки токена

**Результат:** Авторизация работает

---

### ЭТАП 4: Backend API — CRUD ботов
- Создание/редактирование/удаление ботов
- Создание папки и bot.db для каждого бота
- Запуск/остановка ботов (заглушка)

**Результат:** CRUD ботов через API

---

### ЭТАП 5: Backend API — Каналы и тарифы
- CRUD каналов (работа с bot.db конкретного бота)
- CRUD тарифов

**Результат:** Управление каналами и тарифами

---

### ЭТАП 6: Backend API — Промокоды
- CRUD промокодов
- Валидация промокода

**Результат:** Управление промокодами

---

### ЭТАП 7: Backend API — Рассылки
- CRUD рассылок
- Запуск/отмена рассылки
- Статус рассылки

**Результат:** Управление рассылками

---

### ЭТАП 8: Шаблон бота — Ядро
- Aiogram 3 бот
- /start, меню, выбор канала, выбор тарифа
- Подключение к своему bot.db

**Результат:** Базовый бот работает

---

### ЭТАП 9: Шаблон бота — CryptoBot оплата
- Интеграция CryptoBot API
- Создание инвойса
- Обработка webhook

**Результат:** Оплата работает

---

### ЭТАП 10: Userbot — Автодобавление
- Pyrogram client
- Добавление юзера в канал
- Обработка ошибок

**Результат:** Автодобавление работает

---

### ЭТАП 11: Подписки — Проверка и автокик
- Фоновая проверка подписок
- Уведомление об истечении
- Автокик через userbot

**Результат:** Автокик работает

---

### ЭТАП 12: Шаблон бота — Промокоды и рассылки
- Ввод промокода
- Мои подписки
- Получение рассылок

**Результат:** Полный функционал бота

---

### ЭТАП 13: Оркестратор ботов
- Запуск бота как subprocess
- Остановка по PID
- Автозапуск активных ботов

**Результат:** Управление процессами

---

### ЭТАП 14: Админка — Frontend
- React + Tailwind
- Все страницы: логин, дашборд, боты, каналы, тарифы, промокоды, рассылки

**Результат:** Полная админка

---

### ЭТАП 15: Деплой и документация
- Настройка supervisor
- Настройка nginx
- SSL (certbot)
- README с инструкцией

**Результат:** Готово к продакшену

---

## 🔄 WORKFLOW

### Создание бота:
1. Админ вводит токен Telegram бота
2. Система создаёт папку `data/bots/{uuid}/`
3. Система создаёт `bot.db` с таблицами
4. Админ добавляет каналы и тарифы
5. Админ нажимает "Запустить"
6. Оркестратор запускает `python bot_template/run.py --bot-uuid={uuid}`

### Покупка доступа:
1. Юзер /start → меню
2. Выбор канала → тарифы
3. (Промокод) → создание инвойса CryptoBot
4. Оплата → webhook → добавление в канал
5. Запись подписки в bot.db

### Автокик:
1. Фоновая задача проверяет expires_at
2. За день — уведомление
3. При истечении — кик через userbot
4. Обновление is_active = 0

---

## 📝 ВАЖНЫЕ ЗАМЕТКИ

### SQLite особенности:
- Каждый бот = отдельный файл bot.db
- Изоляция данных между ботами
- Простой бэкап (скопировать файл)
- Нет необходимости в отдельном сервере БД

### Запуск без Docker:
```bash
# Установка
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Backend
python backend/run.py

# Userbot
python userbot/run.py

# Frontend (dev)
cd frontend && npm run dev
```

### Supervisor для продакшена:
```ini
[program:bot-constructor-backend]
command=/path/to/venv/bin/python /path/to/backend/run.py
directory=/path/to/project
autostart=true
autorestart=true

[program:bot-constructor-userbot]
command=/path/to/venv/bin/python /path/to/userbot/run.py
directory=/path/to/project
autostart=true
autorestart=true
```

---

**Готов к работе. Жду "Этап 1"!**
