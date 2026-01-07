# ✅ ЧЕК-ЛИСТ: Telegram-бот продажи доступа к каналам

**Версия:** 4.0  
**Платформа:** Windows Server  
**Архитектура:** Один бот, SQLite, без Docker, фиксированный шаблон

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
**Статус:** ⬜ Не начат

### Подготовка репозитория:
- [ ] Очистить от старого кода (если есть)
- [ ] Актуализировать README.md

### Конфигурационные файлы:
- [ ] `.gitignore` (data/, venv/, .env, __pycache__/, node_modules/, logs/)
- [ ] `.env.example` (все переменные: BOT_TOKEN, ADMIN_IDS, кошельки, etc.)
- [ ] `requirements.txt`

### Структура папок:
- [ ] `data/` и `data/backups/`
- [ ] `bot/`, `bot/models/`, `bot/handlers/`, `bot/keyboards/`
- [ ] `bot/callbacks/`, `bot/middlewares/`, `bot/services/`, `bot/locales/`
- [ ] `userbot/`, `userbot/actions/`
- [ ] `admin/`, `admin/api/`, `admin/schemas/`
- [ ] `frontend/`, `scripts/`

### SQLAlchemy модели (`bot/models/`):
- [ ] `__init__.py`, `base.py`
- [ ] `settings.py` — Settings (key-value)
- [ ] `channel.py` — Channel
- [ ] `package.py` — Package, PackageChannel, PackageOption
- [ ] `user.py` — User
- [ ] `subscription.py` — Subscription
- [ ] `payment.py` — Payment
- [ ] `promocode.py` — Promocode, PromocodeUse
- [ ] `text.py` — Text (контент-менеджер)
- [ ] `faq.py` — FAQItem
- [ ] `task.py` — Task (очередь для userbot)
- [ ] `broadcast.py` — Broadcast
- [ ] `admin_log.py` — AdminLog

### База данных:
- [ ] `bot/database.py` — async engine, get_session, init_db
- [ ] `scripts/setup_db.py` — инициализация БД + дефолтные тексты

### Дефолтные тексты (`bot/locales/`):
- [ ] `__init__.py`
- [ ] `ru.py` — все тексты RU
- [ ] `en.py` — все тексты EN
- [ ] Скрипт заполняет таблицу `texts` при первом запуске

### Базовый Backend:
- [ ] `admin/__init__.py`, `admin/config.py`, `admin/database.py`
- [ ] `admin/run.py` — точка входа FastAPI
- [ ] `admin/api/__init__.py` — главный роутер
- [ ] `GET /health` → `{"status": "ok", "database": "connected"}`

### Windows .bat файлы (UTF-8, chcp 65001):
- [ ] `install.bat` — создание venv, pip install, копирование .env, setup_db
- [ ] `start_admin.bat` — запуск FastAPI backend

### Проверка:
```cmd
install.bat
start_admin.bat
:: http://localhost:8000/health → {"status": "ok"}
:: http://localhost:8000/docs → Swagger UI
```

---

## ЧАТ 2: Telegram бот — Ядро
**Статус:** ⬜ Не начат

### Конфигурация и Loader:
- [ ] `bot/__init__.py`, `bot/config.py`
- [ ] `bot/loader.py` — Bot, Dispatcher

### Сервис контента:
- [ ] `bot/services/__init__.py`
- [ ] `bot/services/content.py` — ContentService с кэшем

### Middleware:
- [ ] `bot/middlewares/__init__.py`
- [ ] `bot/middlewares/database.py` — сессия БД
- [ ] `bot/middlewares/user.py` — регистрация юзера + уведомление админам
- [ ] `bot/middlewares/i18n.py` — определение языка
- [ ] `bot/middlewares/ban.py` — проверка бана
- [ ] `bot/middlewares/rate_limit.py` — лимит 30/мин

### Клавиатуры:
- [ ] `bot/keyboards/__init__.py`
- [ ] `bot/keyboards/inline.py`
  - [ ] language_keyboard()
  - [ ] main_menu_keyboard()
  - [ ] packages_keyboard()
  - [ ] package_detail_keyboard()
  - [ ] package_options_keyboard()

### Handlers:
- [ ] `bot/handlers/__init__.py`
- [ ] `bot/handlers/start.py` — /start, выбор языка
- [ ] `bot/handlers/menu.py` — главное меню
- [ ] `bot/handlers/language.py` — смена языка
- [ ] `bot/handlers/packages.py` — список пакетов, детали, варианты

### Callbacks:
- [ ] `bot/callbacks/__init__.py`
- [ ] `bot/callbacks/language.py`
- [ ] `bot/callbacks/package.py`

### Уведомления:
- [ ] `bot/services/notifications.py` — notify_admins()

### Точка входа:
- [ ] `bot/run.py`

### Windows .bat:
- [ ] `start_bot.bat`

### Проверка:
```cmd
start_bot.bat
:: /start → выбор языка → меню
:: Пакеты → список → детали → варианты срока
```

---

## ЧАТ 3: Оплата + Userbot
**Статус:** ⬜ Не начат

### Blockchain API:
- [ ] `bot/services/blockchain.py`
  - [ ] TON: проверка транзакции через toncenter.com
  - [ ] TRC20: проверка транзакции через trongrid.io
  - [ ] verify_transaction(network, tx_hash, expected_amount, wallet)

### Handler и Callbacks оплаты:
- [ ] `bot/handlers/payment.py`
  - [ ] Выбор сети
  - [ ] Показ адреса
  - [ ] Приём hash текстом
  - [ ] Проверка и подтверждение
- [ ] `bot/callbacks/payment.py`

### Сервис подписок:
- [ ] `bot/services/subscription.py`
  - [ ] create_subscription()
  - [ ] activate_subscription()

### Userbot:
- [ ] `userbot/__init__.py`, `userbot/config.py`
- [ ] `userbot/client.py` — Pyrogram Client
- [ ] `userbot/run.py` — основной цикл обработки tasks

### Действия userbot:
- [ ] `userbot/actions/__init__.py`
- [ ] `userbot/actions/invite.py` — invite_to_channels()
- [ ] `userbot/actions/kick.py` — kick_from_channels()

### Windows .bat:
- [ ] `start_userbot.bat`
- [ ] `generate_session.bat`
- [ ] `scripts/generate_session.py`

### Проверка:
```cmd
generate_session.bat
start_userbot.bat
start_bot.bat

:: Полный цикл:
:: Выбрать пакет → срок → сеть → скопировать адрес
:: Оплатить → отправить hash → получить доступ
```

---

## ЧАТ 4: Подписки + фичи
**Статус:** ⬜ Не начат

### Мои подписки:
- [ ] `bot/handlers/subscriptions.py`
  - [ ] Список активных подписок
  - [ ] Кнопка "Ссылки на каналы"
  - [ ] Кнопка "Продлить"
  - [ ] Истёкшие подписки с кнопкой "Возобновить"
- [ ] `bot/callbacks/subscription.py`

### Промокоды:
- [ ] `bot/handlers/promocode.py`
- [ ] `bot/services/promocode.py`

### FAQ:
- [ ] `bot/handlers/faq.py`

### Пробный период:
- [ ] Логика в payment handler
- [ ] Проверка trial_used у юзера
- [ ] Создание trial подписки

### Проверка подписок:
- [ ] `bot/services/subscription_checker.py`
  - [ ] Уведомления за 3 дня
  - [ ] Уведомления за 1 день
  - [ ] Автокик при истечении

### Админ в боте:
- [ ] `bot/handlers/admin.py`
- [ ] `bot/callbacks/admin.py`
  - [ ] /admin, /stats
  - [ ] Поиск юзера
  - [ ] Выдача/отзыв доступа
  - [ ] Бан/разбан
  - [ ] Ручное подтверждение оплаты

### Проверка:
```cmd
:: Мои подписки → ссылки работают
:: Промокод применяется
:: FAQ показывает вопросы/ответы
:: Пробный период активируется
:: /admin → все действия работают
```

---

## ЧАТ 5: Backend API
**Статус:** ⬜ Не начат

### Dashboard:
- [ ] `admin/api/dashboard.py`
  - [ ] GET /api/dashboard/stats
  - [ ] GET /api/dashboard/chart/revenue
  - [ ] GET /api/dashboard/chart/users
  - [ ] GET /api/dashboard/recent

### CRUD:
- [ ] `admin/api/packages.py` + `admin/schemas/package.py`
- [ ] `admin/api/channels.py` + `admin/schemas/channel.py`
- [ ] `admin/api/users.py` + `admin/schemas/user.py` (+ grant/revoke/ban)
- [ ] `admin/api/subscriptions.py` + `admin/schemas/subscription.py`
- [ ] `admin/api/payments.py` + `admin/schemas/payment.py` (+ manual confirm)
- [ ] `admin/api/promocodes.py` + `admin/schemas/promocode.py`
- [ ] `admin/api/content.py` + `admin/schemas/content.py` (texts + FAQ)
- [ ] `admin/api/broadcasts.py` + `admin/schemas/broadcast.py`
- [ ] `admin/api/settings.py` + `admin/schemas/settings.py`

### Экспорт и Бэкапы:
- [ ] `admin/api/export.py` — CSV
- [ ] `admin/api/backup.py`
- [ ] `scripts/backup_db.py`
- [ ] `backup_db.bat`

### Проверка:
```cmd
start_admin.bat
:: http://localhost:8000/docs — все endpoints работают
```

---

## ЧАТ 6: Frontend
**Статус:** ⬜ Не начат

### Базовая структура:
- [ ] `frontend/package.json`, `vite.config.js`, `tailwind.config.js`
- [ ] `frontend/src/main.jsx`, `App.jsx`, `index.css`

### API клиент:
- [ ] `frontend/src/api/` — все модули

### Тёмная тема:
- [ ] `frontend/src/context/ThemeContext.jsx`
- [ ] CSS переменные, localStorage
- [ ] ThemeToggle компонент

### Компоненты:
- [ ] Layout, Sidebar, Header
- [ ] StatsCard, Chart (Recharts)
- [ ] DataTable, Modal, ConfirmDialog

### Страницы:
- [ ] Dashboard с графиками
- [ ] Packages — конструктор пакетов
- [ ] Users (+ выдача/отзыв/бан)
- [ ] Payments (+ ручное подтверждение)
- [ ] Promocodes
- [ ] Content — тексты + FAQ
- [ ] Broadcasts
- [ ] Settings

### Windows .bat:
- [ ] `start_frontend.bat`
- [ ] `start_all.bat`
- [ ] `stop_all.bat`

### Проверка:
```cmd
cd frontend && npm install && npm run dev
:: http://localhost:3000 — Dashboard
:: Тёмная тема переключается
```

---

## 📊 ПРОГРЕСС

| # | Чат | Статус | Описание |
|---|-----|--------|----------|
| 1 | Структура и БД | ⬜ | Папки, модели, FastAPI |
| 2 | Бот — Ядро | ⬜ | /start, меню, пакеты |
| 3 | Оплата + Userbot | ⬜ | TON/TRC20, invite/kick |
| 4 | Подписки + фичи | ⬜ | Промокоды, FAQ, trial, /admin |
| 5 | Backend API | ⬜ | Все endpoints |
| 6 | Frontend | ⬜ | React + тёмная тема |

**Легенда:** ⬜ Не начат | 🔄 В работе | ✅ Готово

**Прогресс:** 0/6 чатов (0%)

---

**Готов. Жду команду "Чат 1"!**
