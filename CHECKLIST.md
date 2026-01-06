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
:: http://localhost:8001/health → {"status": "ok", "database": "connected"}
```

---

## ЧАТ 2: Telegram бот — Ядро
**Статус:** ⬜ Не начат

### Локализация:
- [ ] `bot/locales/__init__.py` — get_text()
- [ ] `bot/locales/ru.py` — все тексты RU
- [ ] `bot/locales/en.py` — все тексты EN

### Конфигурация и Loader:
- [ ] `bot/__init__.py`, `bot/config.py`
- [ ] `bot/loader.py` — Bot, Dispatcher

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
- [ ] tariffs_keyboard(), tariff_detail_keyboard()

### Handlers:
- [ ] `bot/handlers/__init__.py`
- [ ] `bot/handlers/start.py` — /start, deep links
- [ ] `bot/handlers/menu.py` — главное меню
- [ ] `bot/handlers/language.py` — смена языка
- [ ] `bot/handlers/tariffs.py` — список и детали тарифов

### Callbacks:
- [ ] `bot/callbacks/__init__.py`
- [ ] `bot/callbacks/language.py`
- [ ] `bot/callbacks/tariff.py`

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
:: /start в Telegram → выбор языка → меню
```

---

## ЧАТ 3: CryptoBot оплата
**Статус:** ⬜ Не начат

### CryptoBot API:
- [ ] `bot/services/cryptobot.py` — CryptoBotAPI класс
- [ ] create_invoice(), get_invoice(), verify_webhook_signature()

### Handler и Callbacks оплаты:
- [ ] `bot/handlers/payment.py`
- [ ] `bot/callbacks/payment.py`

### Webhook:
- [ ] `admin/api/webhooks.py` — POST /webhooks/cryptobot

### Сервис подписок:
- [ ] `bot/services/subscription.py`

### Проверка:
```cmd
:: Добавить CRYPTOBOT_TOKEN в .env
:: Выбрать тариф → Оплатить → webhook → подписка создана
```

---

## ЧАТ 4: Userbot + Подписки
**Статус:** ⬜ Не начат

### Userbot:
- [ ] `userbot/__init__.py`, `userbot/config.py`
- [ ] `userbot/client.py` — Pyrogram Client
- [ ] `userbot/run.py`

### Действия:
- [ ] `userbot/actions/__init__.py`
- [ ] `userbot/actions/invite.py` — invite_to_channels()
- [ ] `userbot/actions/kick.py` — kick_from_channels()

### Проверка подписок:
- [ ] `bot/services/subscription_checker.py`
- [ ] Уведомления за 3 дня, за 1 день
- [ ] Автокик при истечении

### Windows .bat:
- [ ] `start_userbot.bat`
- [ ] `generate_session.bat`

### Проверка:
```cmd
generate_session.bat
start_userbot.bat
:: После оплаты → юзер в каналах
```

---

## ЧАТ 5: Фичи бота
**Статус:** ⬜ Не начат

### Промокоды:
- [ ] `bot/handlers/promocode.py`
- [ ] `bot/services/promocode.py`

### Мои подписки:
- [ ] `bot/handlers/subscription.py`

### Конструктор меню (навигация в боте):
- [ ] `bot/handlers/menu_navigation.py`
  - Загрузка дерева меню из БД
  - Обработка разделов (подменю)
  - Обработка типов: link, text, faq, system
  - Условия показа (subscribed/not_subscribed/language)
  - Кнопка "Назад" для подменю

### FAQ (Вопросы-ответы):
- [ ] `bot/handlers/faq.py`
  - Показ вопросов в категории
  - Показ ответа

### Админ в боте:
- [ ] `bot/handlers/admin.py`
- [ ] `bot/callbacks/admin.py`
- [ ] /admin, /stats
- [ ] Поиск юзера, выдача/отзыв доступа
- [ ] Бан/разбан
- [ ] Ручное подтверждение оплаты

### Пробный период:
- [ ] Логика trial в оплате

### Проверка:
```cmd
:: /admin → меню работает
:: Промокод применяется
:: Мои подписки показывает список
```

---

## ЧАТ 6: Рассылки
**Статус:** ⬜ Не начат

### Сервис рассылок:
- [ ] `bot/services/broadcast.py`
- [ ] create_broadcast(), start_broadcast(), pause/cancel

### API для админки:
- [ ] `admin/api/broadcasts.py`
- [ ] `admin/schemas/broadcast.py`

### Админ в боте:
- [ ] Быстрая рассылка через /admin

### Проверка:
```cmd
:: /admin → Рассылка → текст → отправлено X из Y
```

---

## ЧАТ 7: Админка — Backend API
**Статус:** ⬜ Не начат

### Dashboard:
- [ ] `admin/api/dashboard.py` — stats, charts, recent

### CRUD:
- [ ] `admin/api/channels.py` + `admin/schemas/channel.py`
- [ ] `admin/api/tariffs.py` + `admin/schemas/tariff.py`
- [ ] `admin/api/users.py` + `admin/schemas/user.py` — + grant/revoke/ban
- [ ] `admin/api/subscriptions.py` + `admin/schemas/subscription.py`
- [ ] `admin/api/payments.py` + `admin/schemas/payment.py` — + manual confirm
- [ ] `admin/api/promocodes.py` + `admin/schemas/promocode.py`
- [ ] `admin/api/menu.py` + `admin/schemas/menu.py` — конструктор меню
- [ ] `admin/api/faq.py` + `admin/schemas/faq.py` — вопросы-ответы
- [ ] `admin/api/settings.py` + `admin/schemas/settings.py`

### Экспорт и Бэкапы:
- [ ] `admin/api/export.py` — CSV
- [ ] `admin/api/backup.py`
- [ ] `scripts/backup_db.py`
- [ ] `backup_db.bat`

### Проверка:
```cmd
start_admin.bat
:: http://localhost:8001/docs — Swagger работает
```

---

## ЧАТ 8: Админка — Frontend
**Статус:** ⬜ Не начат

### Базовая структура:
- [ ] `frontend/package.json`, `vite.config.js`, `tailwind.config.js`
- [ ] `frontend/src/main.jsx`, `App.jsx`, `index.css`

### API клиент:
- [ ] `frontend/src/api/client.js` и все модули

### Тёмная тема:
- [ ] `frontend/src/context/ThemeContext.jsx`
- [ ] CSS переменные, localStorage
- [ ] ThemeToggle компонент

### Компоненты:
- [ ] Layout, Sidebar, Header, ThemeToggle
- [ ] StatsCard, Chart (Recharts), DataTable
- [ ] Modal, ConfirmDialog, ExportButton
- [ ] **DragDropTree** — для конструктора меню
- [ ] **MenuItemForm** — форма элемента меню
- [ ] **MenuPreview** — превью меню как в боте

### Страницы:
- [ ] Dashboard с графиками
- [ ] Channels, Tariffs (CRUD)
- [ ] Users (+ выдача/отзыв/бан)
- [ ] Subscriptions, Payments (+ ручное подтверждение)
- [ ] Promocodes, Broadcasts
- [ ] **MenuBuilder** — конструктор меню (drag-n-drop)
- [ ] **FAQ** — вопросы-ответы
- [ ] Settings, Backups

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
```

---

## 📊 ПРОГРЕСС

| # | Чат | Статус | Описание |
|---|-----|--------|----------|
| 1 | Структура и БД | ✅ | Папки, модели, FastAPI |
| 2 | Бот — Ядро | ⬜ | /start, меню, тарифы, i18n |
| 3 | CryptoBot | ⬜ | Оплата, webhook |
| 4 | Userbot + Подписки | ⬜ | Инвайт, кик, проверка |
| 5 | Фичи бота | ⬜ | Промокоды, админ, trial, **меню, FAQ** |
| 6 | Рассылки | ⬜ | Broadcast система |
| 7 | Backend API | ⬜ | Все endpoints, **menu, faq** |
| 8 | Frontend | ⬜ | React + тёмная тема, **MenuBuilder** |

**Легенда:** ⬜ Не начат | 🔄 В работе | ✅ Готово

**Прогресс:** 1/8 чатов (12.5%)

---

## 🚀 СТАРТ

1. Напиши **"Чат 2"**
2. Claude делает всё из списка
3. Claude выгружает в GitHub
4. Ты проверяешь
5. Пишешь **"Чат 3"** или замечания
6. Повторяем до конца

---

**Чат 1 выполнен! Жду команду "Чат 2"!**
