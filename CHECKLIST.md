# ✅ ЧЕК-ЛИСТ: Конструктор Telegram-ботов

**Архитектура:** Без Docker, SQLite для каждого бота отдельно

---

## КАК РАБОТАЕМ

```
Ты пишешь: "Этап 1" → Я делаю ВСЁ из этапа 1
Ты проверяешь → Пишешь "OK" или замечания
Ты пишешь: "Этап 2" → Я делаю этап 2
... и так до конца
```

---

## ЭТАП 1: Структура проекта
**Статус:** ✅ Готово

### Задачи:
- [x] Создать структуру папок
- [x] requirements.txt (FastAPI, SQLAlchemy, aiosqlite, aiogram, pyrogram, pydantic, python-jose, passlib, httpx)
- [x] .env.example
- [x] backend/run.py (точка входа)
- [x] backend/app/__init__.py
- [x] backend/app/main.py (FastAPI + health check)
- [x] backend/app/config.py (Settings через pydantic)
- [x] backend/app/database.py (async SQLite engine)
- [x] Создать папку data/

---

## ЭТАП 2: База данных — Модели
**Статус:** ✅ Готово

### Задачи:
- [x] backend/app/models/__init__.py
- [x] backend/app/models/main_db.py (Admin, Bot, UserbotConfig)
- [x] backend/app/models/bot_db.py (Channel, Tariff, User, Subscription, Payment, Promocode, Broadcast)
- [x] Функция init_main_db() — создание main.db
- [x] Функция init_bot_db(uuid) — создание bot.db
- [x] Функция get_main_db() — сессия к main.db
- [x] Функция get_bot_db(uuid) — сессия к bot.db
- [x] scripts/create_admin.py — создание первого админа

---

## ЭТАП 3: Backend API — Auth
**Статус:** ✅ Готово

### Задачи:
- [x] backend/app/utils/__init__.py
- [x] backend/app/utils/security.py (hash_password, verify_password, create_token, decode_token)
- [x] backend/app/schemas/__init__.py
- [x] backend/app/schemas/auth.py (LoginRequest, TokenResponse, AdminResponse)
- [x] backend/app/api/__init__.py
- [x] backend/app/api/deps.py (get_db, get_current_admin)
- [x] backend/app/api/auth.py (login, me)
- [x] Подключить роутер в main.py

---

## ЭТАП 4: Backend API — CRUD ботов
**Статус:** ✅ Готово

### Задачи:
- [x] backend/app/schemas/bot.py (BotCreate, BotUpdate, BotResponse)
- [x] backend/app/api/bots.py
- [x] При создании бота — создавать папку data/bots/{uuid}/ и bot.db
- [x] При удалении бота — удалять папку

---

## ЭТАП 5: Backend API — Каналы и тарифы
**Статус:** ✅ Готово

### Задачи:
- [x] backend/app/schemas/channel.py
- [x] backend/app/schemas/tariff.py
- [x] backend/app/api/channels.py (работа с bot.db)
- [x] backend/app/api/tariffs.py

---

## ЭТАП 6: Backend API — Промокоды
**Статус:** ✅ Готово

### Задачи:
- [x] backend/app/schemas/promocode.py
- [x] backend/app/api/promocodes.py
- [x] Валидация: срок, лимит, активность

---

## ЭТАП 7: Backend API — Рассылки
**Статус:** ✅ Готово

### Задачи:
- [x] backend/app/schemas/broadcast.py
- [x] backend/app/api/broadcasts.py
- [x] backend/app/services/__init__.py
- [x] backend/app/services/broadcast_worker.py (фоновая задача)

---

## ЭТАП 8: Шаблон бота — Ядро
**Статус:** ✅ Готово

### Задачи:
- [x] backend/bot_template/__init__.py
- [x] backend/bot_template/run.py (точка входа: `python run.py --bot-uuid=xxx`)
- [x] backend/bot_template/loader.py (Bot, Dispatcher)
- [x] backend/bot_template/config.py (загрузка конфига из main.db)
- [x] backend/bot_template/database.py (подключение к bot.db)
- [x] backend/bot_template/handlers/__init__.py
- [x] backend/bot_template/handlers/start.py
- [x] backend/bot_template/handlers/menu.py
- [x] backend/bot_template/handlers/channels.py
- [x] backend/bot_template/handlers/tariffs.py
- [x] backend/bot_template/keyboards/__init__.py
- [x] backend/bot_template/keyboards/inline.py
- [x] backend/bot_template/keyboards/reply.py

---

## ЭТАП 9: Шаблон бота — CryptoBot оплата
**Статус:** ✅ Готово

### Задачи:
- [x] backend/app/services/cryptobot.py (CryptoBot API client)
- [x] backend/bot_template/handlers/payment.py
- [x] backend/bot_template/callbacks/__init__.py
- [x] backend/bot_template/callbacks/payment.py
- [x] backend/app/api/webhooks.py (webhook от CryptoBot)

### Функционал:
- [x] Создание инвойса (createInvoice)
- [x] Отправка кнопки оплаты юзеру
- [x] Приём webhook при оплате
- [x] Обновление статуса в БД
- [x] Уведомление юзера

### Файлы созданы:
```
backend/
├── app/
│   ├── services/
│   │   ├── __init__.py
│   │   └── cryptobot.py          # CryptoBot API клиент
│   └── api/
│       └── webhooks.py           # Webhook эндпоинт
└── bot_template/
    ├── handlers/
    │   ├── __init__.py           # Обновлён (добавлен payment)
    │   └── payment.py            # Обработчик платежей
    └── callbacks/
        ├── __init__.py           # Роутер callbacks
        └── payment.py            # Deeplink после оплаты

# Патчи для интеграции:
backend/app/main_patch.py         # Пример обновления main.py
backend/bot_template/run_patch.py # Пример обновления run.py
```

### Что нужно интегрировать:
1. В `backend/app/main.py` добавить:
   - `from .api import webhooks`
   - `app.include_router(webhooks.router, prefix="/api")`

2. В `backend/bot_template/run.py` добавить:
   - `from .callbacks import router as callbacks_router`
   - `dp.include_router(callbacks_router)`

3. В `backend/bot_template/handlers/__init__.py`:
   - Добавить `from . import payment`
   - Добавить `router.include_router(payment.router)`

---

## ЭТАП 10: Userbot — Автодобавление
**Статус:** ⬜ Не начат

### Задачи:
- [ ] userbot/requirements.txt (pyrogram, tgcrypto)
- [ ] userbot/run.py
- [ ] userbot/config.py
- [ ] userbot/client.py (Pyrogram Client)
- [ ] userbot/actions/__init__.py
- [ ] userbot/actions/invite.py
- [ ] HTTP API или Redis queue для задач

---

## ЭТАП 11: Подписки — Проверка и автокик
**Статус:** ⬜ Не начат

### Задачи:
- [ ] backend/app/services/subscription_checker.py
- [ ] userbot/actions/kick.py
- [ ] Фоновая задача (asyncio loop или APScheduler)

---

## ЭТАП 12: Шаблон бота — Промокоды и рассылки
**Статус:** ⬜ Не начат

### Задачи:
- [ ] backend/bot_template/handlers/promocode.py
- [ ] backend/bot_template/handlers/subscription.py
- [ ] backend/bot_template/handlers/support.py
- [ ] Интеграция промокода в оплату

---

## ЭТАП 13: Оркестратор ботов
**Статус:** ⬜ Не начат

### Задачи:
- [ ] backend/app/services/bot_manager.py
- [ ] Запуск бота как subprocess
- [ ] Сохранение PID в main.db
- [ ] Остановка по PID
- [ ] Автозапуск активных ботов при старте backend

---

## ЭТАП 14: Админка — Frontend
**Статус:** ⬜ Не начат

### Задачи:
- [ ] frontend/package.json
- [ ] frontend/vite.config.js
- [ ] frontend/tailwind.config.js
- [ ] frontend/index.html
- [ ] frontend/src/main.jsx
- [ ] frontend/src/App.jsx (роутинг)
- [ ] frontend/src/api/client.js (axios)
- [ ] frontend/src/api/auth.js
- [ ] frontend/src/api/bots.js
- [ ] frontend/src/context/AuthContext.jsx
- [ ] frontend/src/pages/Login.jsx
- [ ] frontend/src/pages/Dashboard.jsx
- [ ] frontend/src/pages/Bots/BotList.jsx
- [ ] frontend/src/pages/Bots/BotCreate.jsx
- [ ] frontend/src/pages/Bots/BotEdit.jsx
- [ ] frontend/src/pages/Channels/
- [ ] frontend/src/pages/Tariffs/
- [ ] frontend/src/pages/Promocodes/
- [ ] frontend/src/pages/Broadcasts/
- [ ] frontend/src/components/Layout.jsx
- [ ] frontend/src/components/Sidebar.jsx

---

## ЭТАП 15: Деплой и документация
**Статус:** ⬜ Не начат

### Задачи:
- [ ] scripts/install.sh (установка зависимостей)
- [ ] scripts/supervisor/backend.conf
- [ ] scripts/supervisor/userbot.conf
- [ ] nginx.conf (reverse proxy)
- [ ] Получение SSL (certbot)
- [ ] README.md (полная инструкция)
- [ ] Оптимизация для продакшена

---

## 📊 ПРОГРЕСС

| # | Этап | Статус |
|---|------|--------|
| 1 | Структура проекта | ✅ |
| 2 | База данных — Модели | ✅ |
| 3 | Backend API — Auth | ✅ |
| 4 | Backend API — CRUD ботов | ✅ |
| 5 | Backend API — Каналы и тарифы | ✅ |
| 6 | Backend API — Промокоды | ✅ |
| 7 | Backend API — Рассылки | ✅ |
| 8 | Шаблон бота — Ядро | ✅ |
| 9 | Шаблон бота — CryptoBot оплата | ✅ |
| 10 | Userbot — Автодобавление | ⬜ |
| 11 | Подписки — Проверка и автокик | ⬜ |
| 12 | Шаблон бота — Промокоды и рассылки | ⬜ |
| 13 | Оркестратор ботов | ⬜ |
| 14 | Админка — Frontend | ⬜ |
| 15 | Деплой и документация | ⬜ |

**Легенда:** ⬜ Не начат | 🔄 В работе | ✅ Готово

**Прогресс:** 9/15 этапов (60%)

---

## 🚀 ПРОДОЛЖЕНИЕ

Напиши **"Этап 10"** для продолжения работы.
