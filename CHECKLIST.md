# ✅ ЧЕК-ЛИСТ: Telegram-бот продажи доступа к каналам

**Версия:** 3.0  
**Платформа:** Windows Server  
**Архитектура:** Один бот, SQLite, RU/EN

---

## 📋 КАК РАБОТАЕМ

```
Ты пишешь: "Чат 1" → Я делаю ВСЁ из чата 1
Пушу в GitHub с коммитом
Ты проверяешь → Пишешь "ОК" или замечания
Ты пишешь: "Чат 2" → Я делаю чат 2
... и так до конца
```

---

## ЧАТ 1: Структура и база данных
**Статус:** ⬜ Не начат

### Задачи:

#### Конфигурационные файлы:
- [ ] `.gitignore` (data/, venv/, __pycache__, .env, node_modules/, dist/)
- [ ] `.env.example` — все переменные окружения
- [ ] `requirements.txt` — Python зависимости
- [ ] `README.md` — краткое описание

#### Структура папок:
- [ ] data/, data/backups/, data/logs/
- [ ] bot/, bot/models/, bot/handlers/, bot/keyboards/
- [ ] bot/callbacks/, bot/middlewares/, bot/services/
- [ ] bot/utils/, bot/locales/
- [ ] userbot/, userbot/actions/
- [ ] admin/, admin/api/, admin/schemas/, admin/utils/
- [ ] frontend/, frontend/src/
- [ ] scripts/, bat/

#### SQLAlchemy модели (`bot/models/`):
- [ ] `__init__.py`, `base.py`
- [ ] `settings.py` — Settings (key-value)
- [ ] `channel.py` — Channel
- [ ] `tariff.py` — Tariff, TariffChannel
- [ ] `user.py` — User
- [ ] `subscription.py` — Subscription
- [ ] `payment.py` — Payment
- [ ] `promocode.py` — Promocode, PromocodeUse
- [ ] `broadcast.py` — Broadcast
- [ ] `custom_button.py` — CustomButton
- [ ] `admin_log.py` — AdminLog
- [ ] `analytics.py` — AnalyticsDaily

#### База данных:
- [ ] `bot/database.py` — async engine, get_session, init_db()
- [ ] `scripts/setup_db.py` — инициализация БД

#### Базовый Backend:
- [ ] `admin/run.py`, `admin/config.py`, `admin/database.py`
- [ ] `admin/api/__init__.py`
- [ ] `GET /health`, `GET /api/info`

### Проверка:
```bash
python scripts/setup_db.py
python admin/run.py
# http://localhost:8000/health → {"status": "ok"}
```

**Коммит:** `Чат 1: Структура проекта и модели БД`

---

## ЧАТ 2: Telegram бот — Ядро
**Статус:** ⬜ Не начат

### Задачи:
- [ ] Локализация: `bot/locales/` (ru.py, en.py, __init__.py)
- [ ] Конфиг: `bot/config.py`, `bot/loader.py`
- [ ] Middleware: database, user, i18n, ban, throttling
- [ ] Keyboards: inline.py (language, menu, tariffs, back)
- [ ] Deep Links: `bot/utils/deep_links.py`
- [ ] Handlers: start.py, menu.py, language.py, tariffs.py
- [ ] Callbacks: language.py, tariff.py
- [ ] Services: notifications.py
- [ ] `bot/run.py`

### Проверка:
```bash
python bot/run.py
# /start → язык → меню → тарифы
```

**Коммит:** `Чат 2: Ядро бота, локализация, меню, тарифы`

---

## ЧАТ 3: CryptoBot оплата
**Статус:** ⬜ Не начат

### Задачи:
- [ ] `bot/services/cryptobot.py` — API клиент
- [ ] `admin/api/webhooks.py` — webhook CryptoBot
- [ ] `bot/handlers/payment.py` — создание инвойса
- [ ] `bot/callbacks/payment.py`
- [ ] `bot/services/subscription.py` — создание подписки

### Проверка:
```bash
# Оплата → webhook → подписка создана
```

**Коммит:** `Чат 3: CryptoBot оплата и создание подписок`

---

## ЧАТ 4: Userbot + Подписки
**Статус:** ⬜ Не начат

### Задачи:
- [ ] `userbot/` — Pyrogram client, invite.py, kick.py
- [ ] `bot/services/userbot_client.py` — интеграция
- [ ] `bot/services/subscription_checker.py` — проверка истечения
- [ ] `bot/services/reminder.py` — напоминания
- [ ] `scripts/generate_session.py`
- [ ] Фоновые задачи в bot/run.py

### Проверка:
```bash
# Оплата → инвайт в каналы
# Истечение → напоминание → кик
```

**Коммит:** `Чат 4: Userbot, автоинвайт, проверка подписок, напоминания`

---

## ЧАТ 5: Фичи бота
**Статус:** ⬜ Не начат

### Задачи:
- [ ] Промокоды: handlers/promocode.py, services/promocode.py
- [ ] Мои подписки: handlers/subscription.py, callbacks/subscription.py
- [ ] Кастомные кнопки: handlers/custom_buttons.py
- [ ] Админка в боте: handlers/admin.py, callbacks/admin.py
- [ ] Пробный период
- [ ] Ручное подтверждение оплаты

### Проверка:
```bash
# Промокоды работают
# /admin меню работает
# Ручное подтверждение создаёт подписку
```

**Коммит:** `Чат 5: Промокоды, подписки, кастомные кнопки, админка в боте`

---

## ЧАТ 6: Backend API
**Статус:** ⬜ Не начат

### Задачи:
- [ ] `admin/utils/security.py` — JWT, пароли
- [ ] `admin/api/auth.py` — login, me
- [ ] `admin/api/deps.py` — dependencies
- [ ] `admin/api/dashboard.py` — статистика
- [ ] CRUD: channels, tariffs, users, subscriptions, payments, promocodes, broadcasts, buttons, settings
- [ ] `admin/api/analytics.py` — графики
- [ ] Все schemas/

### Проверка:
```bash
python admin/run.py
# http://localhost:8000/docs → все endpoints
```

**Коммит:** `Чат 6: Backend API — все CRUD endpoints и аналитика`

---

## ЧАТ 7: Frontend React
**Статус:** ⬜ Не начат

### Задачи:
- [ ] package.json, vite.config.js, tailwind.config.js
- [ ] Тёмная тема: ThemeContext.jsx, ThemeToggle.jsx
- [ ] API клиенты: src/api/
- [ ] Компоненты: Layout, Sidebar, Header, DataTable, Modal, Charts/
- [ ] Страницы: Login, Dashboard, Channels, Tariffs, Users, Subscriptions, Payments (с ручным подтверждением), Promocodes, Broadcasts, Buttons, Analytics, Settings
- [ ] App.jsx с роутингом

### Проверка:
```bash
cd frontend && npm run dev
# Тёмная тема работает
# Все CRUD работают
# Графики отображаются
```

**Коммит:** `Чат 7: Frontend React с тёмной темой и аналитикой`

---

## ЧАТ 8: Финализация
**Статус:** ⬜ Не начат

### Задачи:
- [ ] Windows батники (UTF-8): install.bat, start_*.bat, stop_all.bat, backup_db.bat
- [ ] `bot/services/analytics.py` — сбор аналитики
- [ ] Глобальная обработка ошибок
- [ ] README.md — полная документация
- [ ] Тестирование всего флоу

### Проверка:
```cmd
bat\install.bat
bat\start_all.bat
# Все компоненты работают
```

**Коммит:** `Чат 8: Финализация — батники, документация, тестирование`

---

## 📊 ПРОГРЕСС

| # | Чат | Статус | Описание |
|---|-----|--------|----------|
| 1 | Структура и БД | ⬜ | Папки, модели, база |
| 2 | Бот — Ядро | ⬜ | /start, меню, i18n |
| 3 | CryptoBot | ⬜ | Оплата, webhook |
| 4 | Userbot | ⬜ | Инвайт, кик, напоминания |
| 5 | Фичи бота | ⬜ | Промокоды, админка |
| 6 | Backend API | ⬜ | Все endpoints |
| 7 | Frontend | ⬜ | React, тёмная тема |
| 8 | Финализация | ⬜ | Батники, README |

**Легенда:** ⬜ Не начат | 🔄 В работе | ✅ Готово

---

**Готов. Жду команду "Чат 1"!**
