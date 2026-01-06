# ✅ ЧЕК-ЛИСТ: Telegram-бот продажи доступа к каналам

**Версия:** 3.0 (Чистый старт)  
**Платформа:** Windows Server  
**Архитектура:** Один бот, SQLite, без Docker

---

## 📋 КАК РАБОТАЕМ

```
Ты пишешь: "Чат 1" → Claude делает ВСЁ из Чат 1
Ты проверяешь → Пишешь "ОК" или замечания
Ты пишешь: "Чат 2" → Claude делает Чат 2
... и так до конца
```

**После каждого чата Claude:**
1. Создаёт все файлы
2. Выгружает в GitHub репозиторий
3. Обновляет этот CHECKLIST.md
4. Пишет что сделано и как проверить

---

## ЧАТ 1: Структура и база данных
**Статус:** ✅ Готово

### Подготовка репозитория:
- [x] Удалить старые файлы (backend/, frontend/, userbot/, scripts/, *.bat)
- [x] Оставить: README.md (обновить), .gitattributes
- [x] Загрузить: MASTER_PLAN.md, CHECKLIST.md, CLAUDE_INSTRUCTION.md

### Конфигурационные файлы:
- [x] `.gitignore` (data/, venv/, .env, __pycache__/, node_modules/, logs/)
- [x] `.env.example` (все переменные)
- [x] `requirements.txt`

### Структура папок:
- [x] `data/` и `data/backups/`
- [x] `bot/`, `bot/models/`, `bot/handlers/`, `bot/keyboards/`
- [x] `bot/callbacks/`, `bot/middlewares/`, `bot/services/`, `bot/locales/`
- [x] `userbot/`, `userbot/actions/`
- [x] `admin/`, `admin/api/`, `admin/schemas/`
- [x] `frontend/`, `scripts/`

### SQLAlchemy модели (`bot/models/`):
- [x] `__init__.py`, `base.py`
- [x] `settings.py` — Settings (key-value)
- [x] `channel.py` — Channel
- [x] `tariff.py` — Tariff, TariffChannel
- [x] `user.py` — User
- [x] `subscription.py` — Subscription
- [x] `payment.py` — Payment
- [x] `promocode.py` — Promocode, PromocodeUse
- [x] `broadcast.py` — Broadcast
- [x] `menu_item.py` — MenuItem (конструктор меню)
- [x] `faq_item.py` — FAQItem (вопросы-ответы)
- [x] `admin_log.py` — AdminLog

### База данных:
- [x] `bot/database.py` — async engine, get_session, init_db
- [x] `scripts/setup_db.py` — инициализация БД

### Базовый Backend:
- [x] `admin/__init__.py`, `admin/config.py`, `admin/database.py`
- [x] `admin/run.py` — точка входа FastAPI
- [x] `admin/api/__init__.py` — главный роутер
- [x] `GET /health` → `{"status": "ok", "database": "connected"}`

### Windows .bat файлы (UTF-8, chcp 65001):
- [x] `install.bat` — создание venv, pip install, копирование .env, setup_db
- [x] `start_admin.bat` — запуск FastAPI backend

### README.md:
- [x] Обновить с новым описанием проекта

### Проверка:
```cmd
install.bat
start_admin.bat
:: http://localhost:8000/health → {"status": "ok"}
```

---

## ЧАТ 2: Telegram бот — Ядро
**Статус:** ✅ Готово

### Локализация:
- [x] `bot/locales/__init__.py` — get_text()
- [x] `bot/locales/ru.py` — все тексты RU
- [x] `bot/locales/en.py` — все тексты EN

### Конфигурация и Loader:
- [x] `bot/__init__.py`, `bot/config.py`
- [x] `bot/loader.py` — Bot, Dispatcher

### Middleware:
- [x] `bot/middlewares/__init__.py`
- [x] `bot/middlewares/database.py` — сессия БД
- [x] `bot/middlewares/user.py` — регистрация юзера + уведомление админам
- [x] `bot/middlewares/i18n.py` — определение языка
- [x] `bot/middlewares/ban.py` — проверка бана
- [x] `bot/middlewares/rate_limit.py` — лимит 30/мин

### Клавиатуры:
- [x] `bot/keyboards/__init__.py`, `bot/keyboards/inline.py`
- [x] language_keyboard(), main_menu_keyboard()
- [x] tariffs_keyboard(), tariff_detail_keyboard()

### Handlers:
- [x] `bot/handlers/__init__.py`
- [x] `bot/handlers/start.py` — /start, deep links
- [x] `bot/handlers/menu.py` — главное меню
- [x] `bot/handlers/language.py` — смена языка
- [x] `bot/handlers/tariffs.py` — список и детали тарифов

### Callbacks:
- [x] `bot/callbacks/__init__.py`
- [x] `bot/callbacks/language.py`
- [x] `bot/callbacks/tariff.py`

### Сервисы:
- [x] `bot/services/__init__.py`
- [x] `bot/services/notifications.py` — notify_admins()

### Точка входа:
- [x] `bot/run.py`

### Windows .bat:
- [x] `start_bot.bat`

### Проверка:
```cmd
start_bot.bat
:: /start в Telegram → выбор языка → меню
```

---

## ЧАТ 3: CryptoBot оплата
**Статус:** ✅ Готово

### CryptoBot API:
- [x] `bot/services/cryptobot.py` — CryptoBotAPI класс
- [x] create_invoice(), get_invoice(), verify_webhook_signature()

### Handler и Callbacks оплаты:
- [x] `bot/handlers/payment.py`
- [x] `bot/callbacks/payment.py`

### Webhook:
- [x] `admin/api/webhooks.py` — POST /webhooks/cryptobot

### Сервис подписок:
- [x] `bot/services/subscription.py`

### Проверка:
```cmd
:: Добавить CRYPTOBOT_TOKEN в .env
:: Выбрать тариф → Оплатить → webhook → подписка создана
```

---

## ЧАТ 4: Userbot + Подписки
**Статус:** ✅ Готово

### Userbot:
- [x] `userbot/__init__.py`, `userbot/config.py`
- [x] `userbot/client.py` — Pyrogram Client
- [x] `userbot/run.py`

### Действия:
- [x] `userbot/actions/__init__.py`
- [x] `userbot/actions/invite.py` — invite_to_channels()
- [x] `userbot/actions/kick.py` — kick_from_channels()

### Проверка подписок:
- [x] `bot/services/subscription_checker.py`
- [x] Уведомления за 3 дня, за 1 день
- [x] Автокик при истечении

### Windows .bat:
- [x] `start_userbot.bat`
- [x] `generate_session.bat`

### Проверка:
```cmd
generate_session.bat
start_userbot.bat
:: После оплаты → юзер в каналах
```

---

## ЧАТ 5: Фичи бота
**Статус:** ✅ Готово

### Промокоды:
- [x] `bot/handlers/promocode.py`
- [x] `bot/services/promocode.py`

### Мои подписки:
- [x] `bot/handlers/subscription.py`

### Конструктор меню (навигация в боте):
- [x] `bot/handlers/menu_navigation.py`
  - Загрузка дерева меню из БД
  - Обработка разделов (подменю)
  - Обработка типов: link, text, faq, system
  - Условия показа (subscribed/not_subscribed/language)
  - Кнопка "Назад" для подменю

### FAQ (Вопросы-ответы):
- [x] `bot/handlers/faq.py`
  - Показ вопросов в категории
  - Показ ответа

### Админ в боте:
- [x] `bot/handlers/admin.py`
- [x] `bot/callbacks/admin.py`
- [x] /admin, /stats
- [x] Поиск юзера, выдача/отзыв доступа
- [x] Бан/разбан
- [x] Ручное подтверждение оплаты

### Пробный период:
- [x] Логика trial в оплате

### Проверка:
```cmd
:: /admin → меню работает
:: Промокод применяется
:: Мои подписки показывает список
```

---

## ЧАТ 6: Рассылки
**Статус:** ✅ Готово

### Сервис рассылок:
- [x] `bot/services/broadcast.py`
- [x] create_broadcast(), start_broadcast(), pause/cancel

### API для админки:
- [x] `admin/api/broadcasts.py`
- [x] `admin/schemas/broadcast.py`

### Админ в боте:
- [x] Быстрая рассылка через /admin

### Проверка:
```cmd
:: /admin → Рассылка → текст → отправлено X из Y
```

---

## ЧАТ 7: Админка — Backend API
**Статус:** ✅ Готово

### Dashboard:
- [x] `admin/api/dashboard.py` — stats, charts, recent

### CRUD:
- [x] `admin/api/channels.py` + `admin/schemas/channel.py`
- [x] `admin/api/tariffs.py` + `admin/schemas/tariff.py`
- [x] `admin/api/users.py` + `admin/schemas/user.py` — + grant/revoke/ban
- [x] `admin/api/subscriptions.py` + `admin/schemas/subscription.py`
- [x] `admin/api/payments.py` + `admin/schemas/payment.py` — + manual confirm
- [x] `admin/api/promocodes.py` + `admin/schemas/promocode.py`
- [x] `admin/api/menu.py` + `admin/schemas/menu.py` — конструктор меню
- [x] `admin/api/faq.py` + `admin/schemas/faq.py` — вопросы-ответы
- [x] `admin/api/settings.py` + `admin/schemas/settings.py`

### Экспорт и Бэкапы:
- [x] `admin/api/export.py` — CSV
- [x] `admin/api/backup.py`
- [x] `scripts/backup_db.py`
- [x] `backup_db.bat`

### Проверка:
```cmd
start_admin.bat
:: http://localhost:8000/docs — Swagger работает
```

---

## ЧАТ 8: Админка — Frontend
**Статус:** ✅ Готово

### Базовая структура:
- [x] `frontend/package.json`, `vite.config.js`, `tailwind.config.js`
- [x] `frontend/src/main.jsx`, `App.jsx`, `index.css`

### API клиент:
- [x] `frontend/src/api/client.js` и все модули

### Тёмная тема:
- [x] `frontend/src/context/ThemeContext.jsx`
- [x] CSS переменные, localStorage
- [x] ThemeToggle компонент

### Компоненты:
- [x] Layout, Sidebar, Header, ThemeToggle
- [x] StatsCard, Chart (Recharts), DataTable
- [x] Modal, ConfirmDialog, ExportButton
- [x] **DragDropTree** — для конструктора меню
- [x] **MenuItemForm** — форма элемента меню
- [x] **MenuPreview** — превью меню как в боте

### Страницы:
- [x] Dashboard с графиками
- [x] Channels, Tariffs (CRUD)
- [x] Users (+ выдача/отзыв/бан)
- [x] Subscriptions, Payments (+ ручное подтверждение)
- [x] Promocodes, Broadcasts
- [x] **MenuBuilder** — конструктор меню (drag-n-drop)
- [x] **FAQ** — вопросы-ответы
- [x] Settings, Backups

### Windows .bat:
- [x] `start_frontend.bat`
- [x] `start_all.bat`
- [x] `stop_all.bat`
- [x] `build_frontend.bat`

### Проверка:
```cmd
cd frontend && npm install && npm run dev
:: http://localhost:3000 — Dashboard с графиками
:: Тёмная тема переключается
```

---

## 📊 ПРОГРЕСС

| # | Чат | Статус | Описание |
|---|-----|--------|----------|
| 1 | Структура и БД | ✅ | Папки, модели, FastAPI |
| 2 | Бот — Ядро | ✅ | /start, меню, тарифы, i18n |
| 3 | CryptoBot | ✅ | Оплата, webhook |
| 4 | Userbot + Подписки | ✅ | Инвайт, кик, проверка |
| 5 | Фичи бота | ✅ | Промокоды, админ, trial, **меню, FAQ** |
| 6 | Рассылки | ✅ | Broadcast система |
| 7 | Backend API | ✅ | Все endpoints, **menu, faq** |
| 8 | Frontend | ✅ | React + тёмная тема, **MenuBuilder** |

**Легенда:** ⬜ Не начат | 🔄 В работе | ✅ Готово

**Прогресс:** 8/8 чатов (100%) 🎉

---

## 🚀 ЗАПУСК ПРОЕКТА

### Быстрый старт (Windows):
```cmd
:: 1. Клонировать репозиторий
git clone https://github.com/ironsan2kk-pixel/TGconst.git
cd TGconst

:: 2. Установка
install.bat

:: 3. Настроить .env
:: Открыть .env и заполнить BOT_TOKEN, ADMIN_IDS

:: 4. Запустить всё
start_all.bat
```

### Доступы:
- **Admin Panel:** http://localhost:3000
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

---

## 📁 СТРУКТУРА ФАЙЛОВ

```
telegram-channel-bot/
├── .env.example          # Шаблон переменных окружения
├── .gitignore            # Игнорируемые файлы
├── requirements.txt      # Python зависимости
├── README.md             # Документация
├── MASTER_PLAN.md        # Мастер-план проекта
├── CHECKLIST.md          # Этот чеклист
├── CLAUDE_INSTRUCTION.md # Инструкции для Claude
│
├── install.bat           # Установка проекта
├── start_bot.bat         # Запуск Telegram бота
├── start_admin.bat       # Запуск Backend API
├── start_userbot.bat     # Запуск Pyrogram userbot
├── start_frontend.bat    # Запуск React dev server
├── start_all.bat         # Запуск всех компонентов
├── stop_all.bat          # Остановка всех процессов
├── backup_db.bat         # Бэкап базы данных
├── generate_session.bat  # Генерация Pyrogram session
├── build_frontend.bat    # Сборка frontend для production
│
├── data/                 # База данных и бэкапы
│   ├── bot.db
│   └── backups/
│
├── bot/                  # Telegram бот (Aiogram 3)
│   ├── models/           # SQLAlchemy модели
│   ├── handlers/         # Обработчики команд
│   ├── keyboards/        # Клавиатуры
│   ├── callbacks/        # Callback handlers
│   ├── middlewares/      # Middleware
│   ├── services/         # Бизнес-логика
│   └── locales/          # Локализация
│
├── userbot/              # Pyrogram userbot
│   └── actions/          # Invite/Kick
│
├── admin/                # Backend API (FastAPI)
│   ├── api/              # Endpoints
│   └── schemas/          # Pydantic schemas
│
├── frontend/             # React админка
│   └── src/
│       ├── api/          # API клиент
│       ├── components/   # UI компоненты
│       ├── context/      # React контексты
│       └── pages/        # Страницы
│
└── scripts/              # Утилиты
    ├── setup_db.py
    └── backup_db.py
```

---

**🎉 ПРОЕКТ ЗАВЕРШЁН!**
