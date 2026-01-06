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

---

## 📊 ПРОГРЕСС

| # | Чат | Статус | Описание |
|---|-----|--------|----------|
| 1 | Структура и БД | ✅ | Папки, модели, FastAPI |
| 2 | Бот — Ядро | ✅ | /start, меню, тарифы, i18n |
| 3 | CryptoBot | ✅ | Оплата, webhook |
| 4 | Userbot + Подписки | ✅ | Инвайт, кик, проверка |
| 5 | Фичи бота | ✅ | Промокоды, админ, trial, меню, FAQ |
| 6 | Рассылки | ✅ | Broadcast система |
| 7 | Backend API | ✅ | Все endpoints, menu, faq |
| 8 | Frontend | ⬜ | React + тёмная тема, MenuBuilder |

**Легенда:** ⬜ Не начат | 🔄 В работе | ✅ Готово

**Прогресс:** 7/8 чатов (87.5%)

---

## 🚀 СТАРТ

1. Напиши **"Чат 8"**
2. Claude делает всё из списка
3. Claude выгружает в GitHub
4. Ты проверяешь
5. Проект готов!

---

**Готов. Жду команду "Чат 8"!**
