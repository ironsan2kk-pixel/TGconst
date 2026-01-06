# 🤖 Telegram Channel Bot

Telegram-бот для продажи доступа к приватным каналам через криптовалюту (CryptoBot/USDT).

## ✨ Возможности

- 📺 **Пакеты каналов** — один тариф = доступ к нескольким каналам
- 💳 **CryptoBot оплата** — USDT через CryptoBot API
- 🌐 **Два языка** — русский и английский с переключением
- 🎁 **Промокоды** — скидки процентом или фиксированной суммой
- ⏱️ **Пробный период** — опционально для каждого тарифа
- 🔗 **Deep Links** — прямые ссылки на тарифы
- 📊 **Админ-панель** — React с тёмной темой и графиками
- 🛠️ **Конструктор меню** — настройка кнопок бота
- 📨 **Рассылки** — фильтры по подписке и языку
- 🔔 **Уведомления** — о новых юзерах и оплатах

## 🏗️ Архитектура

```
┌────────────────────────────────────────────────┐
│          АДМИН-ПАНЕЛЬ (React)                  │
│  🌓 Тёмная тема │ 📊 Графики │ 📋 CRUD        │
└────────────────────────┬───────────────────────┘
                         │ REST API
                         ▼
┌────────────────────────────────────────────────┐
│               BACKEND (FastAPI)                │
│  ┌──────────────────────────────────────────┐  │
│  │           bot.db (SQLite)                │  │
│  └──────────────────────────────────────────┘  │
└────────────────────────┬───────────────────────┘
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
    ┌──────────┐  ┌───────────┐  ┌───────────┐
    │ TELEGRAM │  │ CRYPTOBOT │  │  USERBOT  │
    │   BOT    │  │    API    │  │ (Pyrogram)│
    │ (Aiogram)│  │  Платежи  │  │  Инвайты  │
    └──────────┘  └───────────┘  └───────────┘
```

## 🚀 Быстрый старт (Windows)

```cmd
:: 1. Клонировать репозиторий
git clone https://github.com/ironsan2kk-pixel/TGconst.git
cd TGconst

:: 2. Установка
install.bat

:: 3. Настроить .env
:: Открыть .env и заполнить BOT_TOKEN, ADMIN_IDS

:: 4. Запустить админку
start_admin.bat
```

## 📁 Структура проекта

```
telegram-channel-bot/
├── bot/                    # Telegram бот (Aiogram 3)
│   ├── models/             # SQLAlchemy модели
│   ├── handlers/           # Обработчики команд
│   ├── keyboards/          # Клавиатуры
│   ├── middlewares/        # Middleware
│   ├── services/           # Бизнес-логика
│   └── locales/            # Локализация
├── userbot/                # Pyrogram userbot
├── admin/                  # Backend API (FastAPI)
│   ├── api/                # Эндпоинты
│   └── schemas/            # Pydantic схемы
├── frontend/               # React админка
├── data/                   # База данных
├── scripts/                # Утилиты
└── *.bat                   # Windows скрипты
```

## 🛠️ Технологии

| Компонент | Технология |
|-----------|------------|
| Backend API | FastAPI |
| ORM | SQLAlchemy 2.0 + aiosqlite |
| Telegram Bot | Aiogram 3 |
| Userbot | Pyrogram |
| Frontend | React + Tailwind CSS |
| Графики | Recharts |

## 📋 .bat файлы

| Файл | Описание |
|------|----------|
| `install.bat` | Установка (venv, pip, БД) |
| `start_bot.bat` | Запуск Telegram бота |
| `start_admin.bat` | Запуск админ-панели |
| `start_userbot.bat` | Запуск Pyrogram userbot |
| `start_frontend.bat` | Запуск React dev server |
| `start_all.bat` | Запуск всех компонентов |
| `stop_all.bat` | Остановка всех процессов |

## 📖 Документация

- [MASTER_PLAN.md](MASTER_PLAN.md) — полное описание проекта
- [CHECKLIST.md](CHECKLIST.md) — чек-лист разработки
- [CLAUDE_INSTRUCTION.md](CLAUDE_INSTRUCTION.md) — инструкция для Claude

## 📄 Лицензия

MIT License
