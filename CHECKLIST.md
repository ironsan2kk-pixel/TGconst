# ✅ ЧЕК-ЛИСТ: Telegram-бот продажи доступа к каналам

**Версия:** 4.0  
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

## ЧАТ 1: Структура + База данных
**Статус:** ⬜ Не начат

### Конфигурационные файлы:
- [ ] `.gitignore` (data/, venv/, .env, __pycache__/, node_modules/, logs/)
- [ ] `.env.example` (все переменные: BOT_TOKEN, ADMIN_IDS, кошельки)
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
- [ ] `wallet.py` — Wallet (TON/TRC20 адреса)
- [ ] `channel.py` — Channel
- [ ] `package.py` — Package, PackageChannel, PackageOption
- [ ] `user.py` — User
- [ ] `subscription.py` — Subscription
- [ ] `payment.py` — Payment
- [ ] `promocode.py` — Promocode, PromocodeUse
- [ ] `text.py` — Text (контент-менеджер)
- [ ] `faq.py` — FAQItem
- [ ] `broadcast.py` — Broadcast
- [ ] `task.py` — Task (очередь для userbot)
- [ ] `admin_log.py` — AdminLog

### База данных:
- [ ] `bot/database.py` — async engine, get_session, init_db
- [ ] `scripts/setup_db.py` — инициализация БД + дефолтные тексты

### Базовый Backend:
- [ ] `admin/__init__.py`, `admin/config.py`, `admin/database.py`
- [ ] `admin/run.py` — точка входа FastAPI
- [ ] `admin/api/__init__.py` — главный роутер
- [ ] `GET /health` → `{"status": "ok", "database": "connected"}`

### Windows .bat файлы (UTF-8, chcp 65001):
- [ ] `install.bat` — создание venv, pip install, копирование .env, setup_db
- [ ] `start_admin.bat` — запуск FastAPI backend

### README.md:
- [ ] Обновить с новым описанием проекта

### Проверка:
```cmd
install.bat
start_admin.bat
:: http://localhost:8000/health → {"status": "ok"}
```

---

## ЧАТ 2: Telegram бот — Ядро
**Статус:** ⬜ Не начат

### Конфигурация и Loader:
- [ ] `bot/__init__.py`, `bot/config.py`
- [ ] `bot/loader.py` — Bot, Dispatcher

### Сервис контента:
- [ ] `bot/services/content.py` — ContentService (тексты из БД с кэшем)

### Локализация (дефолтные значения):
- [ ] `bot/locales/__init__.py`
- [ ] `bot/locales/ru.py` — все тексты RU
- [ ] `bot/locales/en.py` — все тексты EN

### Middleware:
- [ ] `bot/middlewares/__init__.py`
- [ ] `bot/middlewares/database.py` — сессия БД
- [ ] `bot/middlewares/user.py` — регистрация юзера + уведомление админам
- [ ] `bot/middlewares/i18n.py` — определение языка
- [ ] `bot/middlewares/ban.py` — проверка бана
- [ ] `bot/middlewares/rate_limit.py` — лимит 30/мин

### Клавиатуры:
- [ ] `bot/keyboards/__init__.py`, `bot/keyboards/inline.py`
- [ ] language_keyboard(), main_menu_keyboard()
- [ ] packages_keyboard(), package_detail_keyboard()
- [ ] package_options_keyboard()

### Handlers:
- [ ] `bot/handlers/__init__.py`
- [ ] `bot/handlers/start.py` — /start, выбор языка
- [ ] `bot/handlers/menu.py` — главное меню
- [ ] `bot/handlers/language.py` — смена языка
- [ ] `bot/handlers/packages.py` — список пакетов, детали, выбор срока

### Callbacks:
- [ ] `bot/callbacks/__init__.py`
- [ ] `bot/callbacks/language.py`
- [ ] `bot/callbacks/package.py`

### Сервисы:
- [ ] `bot/services/__init__.py`
- [ ] `bot/services/notifications.py` — notify_admins()

### Точка входа:
- [ ] `bot/run.py`

### Windows .bat:
- [ ] `start_bot.bat`

### Проверка:
```cmd
start_bot.bat
:: /start в Telegram → выбор языка → меню → пакеты
```

---

## ЧАТ 3: Оплата + Userbot
**Статус:** ⬜ Не начат

### Blockchain API:
- [ ] `bot/services/blockchain.py` — BlockchainService
- [ ] check_ton_transaction() — проверка TON через toncenter
- [ ] check_trc20_transaction() — проверка TRC20 через trongrid

### Handler и Callbacks оплаты:
- [ ] `bot/handlers/payment.py` — выбор сети, показ адреса, приём hash
- [ ] `bot/callbacks/payment.py`

### Сервис подписок:
- [ ] `bot/services/subscription.py` — create_subscription(), activate()

### Userbot:
- [ ] `userbot/__init__.py`, `userbot/config.py`
- [ ] `userbot/client.py` — Pyrogram Client
- [ ] `userbot/run.py`
- [ ] `userbot/task_processor.py` — обработка очереди tasks

### Действия:
- [ ] `userbot/actions/__init__.py`
- [ ] `userbot/actions/invite.py` — invite_to_channels()
- [ ] `userbot/actions/kick.py` — kick_from_channels()

### Scripts:
- [ ] `scripts/generate_session.py`

### Windows .bat:
- [ ] `start_userbot.bat`
- [ ] `generate_session.bat`

### Проверка:
```cmd
generate_session.bat
start_userbot.bat
:: Выбрать пакет → срок → сеть → адрес → отправить hash → проверка → доступ
```

---

## ЧАТ 4: Подписки + Фичи
**Статус:** ⬜ Не начат

### Мои подписки:
- [ ] `bot/handlers/subscription.py` — список подписок, ссылки на каналы
- [ ] `bot/callbacks/subscription.py` — показ ссылок, продление

### Промокоды:
- [ ] `bot/handlers/promocode.py`
- [ ] `bot/services/promocode.py` — apply_promocode()

### FAQ:
- [ ] `bot/handlers/faq.py` — список вопросов, показ ответа
- [ ] `bot/callbacks/faq.py`

### Пробный период:
- [ ] Логика trial в payment flow
- [ ] Проверка user.trial_used

### Проверка подписок:
- [ ] `bot/services/subscription_checker.py`
- [ ] Уведомления за 3 дня, за 1 день
- [ ] Автокик при истечении
- [ ] Обновление статуса подписки

### Админ в боте:
- [ ] `bot/handlers/admin.py`
- [ ] `bot/callbacks/admin.py`
- [ ] /admin, /stats
- [ ] Поиск юзера, выдача/отзыв доступа
- [ ] Бан/разбан
- [ ] Ручное подтверждение оплаты

### Проверка:
```cmd
:: "Мои подписки" → ссылки на каналы
:: Промокод применяется
:: FAQ работает
:: /admin → меню работает
```

---

## ЧАТ 5: Backend API
**Статус:** ⬜ Не начат

### Dashboard:
- [ ] `admin/api/dashboard.py` — stats, charts data, recent events

### CRUD Пакеты:
- [ ] `admin/api/packages.py` — пакеты + каналы + варианты
- [ ] `admin/api/channels.py` — отдельно каналы
- [ ] `admin/schemas/package.py`, `admin/schemas/channel.py`

### CRUD Юзеры:
- [ ] `admin/api/users.py` — + grant/revoke/ban
- [ ] `admin/schemas/user.py`

### CRUD Подписки и Платежи:
- [ ] `admin/api/subscriptions.py`
- [ ] `admin/api/payments.py` — + manual confirm
- [ ] `admin/schemas/subscription.py`, `admin/schemas/payment.py`

### CRUD Промокоды:
- [ ] `admin/api/promocodes.py`
- [ ] `admin/schemas/promocode.py`

### Контент:
- [ ] `admin/api/content.py` — texts + faq CRUD
- [ ] `admin/schemas/content.py`

### Настройки:
- [ ] `admin/api/settings.py` — + wallets
- [ ] `admin/schemas/settings.py`

### Рассылки:
- [ ] `admin/api/broadcasts.py`
- [ ] `admin/schemas/broadcast.py`

### Экспорт и Бэкапы:
- [ ] `admin/api/export.py` — CSV (users, payments)
- [ ] `admin/api/backup.py`
- [ ] `scripts/backup_db.py`
- [ ] `backup_db.bat`

### Проверка:
```cmd
start_admin.bat
:: http://localhost:8000/docs — Swagger полный
:: Все endpoints работают
```

---

## ЧАТ 6: Frontend (React админка)
**Статус:** ⬜ Не начат

### Базовая структура:
- [ ] `frontend/package.json`, `vite.config.js`, `tailwind.config.js`
- [ ] `frontend/src/main.jsx`, `App.jsx`, `index.css`

### API клиент:
- [ ] `frontend/src/api/client.js`
- [ ] `frontend/src/api/dashboard.js`
- [ ] `frontend/src/api/packages.js`
- [ ] `frontend/src/api/users.js`
- [ ] `frontend/src/api/payments.js`
- [ ] `frontend/src/api/promocodes.js`
- [ ] `frontend/src/api/content.js`
- [ ] `frontend/src/api/settings.js`
- [ ] `frontend/src/api/broadcasts.js`

### Тёмная тема:
- [ ] `frontend/src/context/ThemeContext.jsx`
- [ ] CSS переменные, localStorage
- [ ] ThemeToggle компонент

### Компоненты:
- [ ] Layout, Sidebar, Header, ThemeToggle
- [ ] StatsCard, Chart (Recharts), DataTable
- [ ] Modal, ConfirmDialog
- [ ] PackageBuilder — конструктор пакетов

### Страницы:
- [ ] Dashboard — с графиками дохода и юзеров
- [ ] Packages — конструктор (каналы + варианты)
- [ ] Users — список + выдача/отзыв/бан
- [ ] Payments — история + ручное подтверждение
- [ ] Promocodes — CRUD
- [ ] Content — тексты + FAQ
- [ ] Settings — настройки + кошельки
- [ ] Broadcasts — рассылки

### Windows .bat:
- [ ] `start_frontend.bat`
- [ ] `start_all.bat`
- [ ] `stop_all.bat`
- [ ] `build_frontend.bat`

### Проверка:
```cmd
cd frontend && npm install && npm run dev
:: http://localhost:3000 — Dashboard с графиками
:: Тёмная тема переключается
:: Все страницы работают
```

---

## 📊 ПРОГРЕСС

| # | Чат | Статус | Описание |
|---|-----|--------|----------|
| 1 | Структура + БД | ⬜ | Папки, модели, FastAPI |
| 2 | Бот — Ядро | ⬜ | /start, меню, пакеты, i18n |
| 3 | Оплата + Userbot | ⬜ | TON/TRC20, invite |
| 4 | Подписки + Фичи | ⬜ | Промокоды, FAQ, trial, автокик |
| 5 | Backend API | ⬜ | Все endpoints |
| 6 | Frontend | ⬜ | React + тёмная тема |

**Легенда:** ⬜ Не начат | 🔄 В работе | ✅ Готово

**Прогресс:** 0/6 чатов (0%)

---

## 🚀 СТАРТ

1. Напиши **"Чат 1"**
2. Claude делает всё из списка
3. Claude выгружает в GitHub
4. Ты проверяешь
5. Пишешь **"Чат 2"** или замечания
6. Повторяем до конца

---

**Готов. Жду команду "Чат 1"!**
