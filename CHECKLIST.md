# ✅ ЧЕК-ЛИСТ: Конструктор Telegram-ботов

**Архитектура:** Без Docker, SQLite для каждого бота отдельно

---

## ⚡ ПЛАН РАБОТЫ ПО ЭТАПАМ

```
1️⃣ Пользователь пишет "Этап N" + "поехали"
2️⃣ Claude создаёт все файлы этапа
3️⃣ Claude ВЫГРУЖАЕТ ВСЁ В РЕПОЗИТОРИЙ
4️⃣ Claude пишет: "проверим"
5️⃣ Пользователь пишет: "проверка"
6️⃣ Claude проверяет работоспособность
7️⃣ Claude обновляет этот CHECKLIST.md (отмечает ✅)
8️⃣ Переход к следующему этапу
```

---

## 📊 ПРОГРЕСС

| # | Этап | Статус |
|---|------|--------|
| 1 | Структура проекта | ✅ Готов |
| 2 | База данных — Модели | ⬜ |
| 3 | Backend API — Auth | ⬜ |
| 4 | Backend API — CRUD ботов | ⬜ |
| 5 | Backend API — Каналы и тарифы | ⬜ |
| 6 | Backend API — Промокоды | ⬜ |
| 7 | Backend API — Рассылки | ⬜ |
| 8 | Шаблон бота — Ядро | ⬜ |
| 9 | Шаблон бота — CryptoBot оплата | ⬜ |
| 10 | Userbot — Автодобавление | ⬜ |
| 11 | Подписки — Проверка и автокик | ⬜ |
| 12 | Шаблон бота — Промокоды и рассылки | ⬜ |
| 13 | Оркестратор ботов | ⬜ |
| 14 | Админка — Frontend | ⬜ |
| 15 | Деплой и документация | ⬜ |

---

## ЭТАП 1: Структура проекта
**Статус:** ✅ Готов

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

### Проверка:
```bash
python backend/run.py
# http://localhost:8000/health → {"status": "ok"}
```

### Файлы:
```
TGconst/
├── requirements.txt
├── .env.example
├── data/
├── backend/
│   ├── run.py
│   └── app/
│       ├── __init__.py
│       ├── main.py
│       ├── config.py
│       └── database.py
```

---

## ЭТАП 2: База данных — Модели
**Статус:** ⬜ Не начат

### Задачи:
- [ ] backend/app/models/__init__.py
- [ ] backend/app/models/main_db.py (Admin, Bot, UserbotConfig)
- [ ] backend/app/models/bot_db.py (Channel, Tariff, User, Subscription, Payment, Promocode, Broadcast)
- [ ] Функция init_main_db() — создание main.db
- [ ] Функция init_bot_db(uuid) — создание bot.db
- [ ] Функция get_main_db() — сессия к main.db
- [ ] Функция get_bot_db(uuid) — сессия к bot.db
- [ ] scripts/create_admin.py — создание первого админа

### Проверка:
```bash
python scripts/create_admin.py
# Создаётся data/main.db с таблицами и админом
```

### Файлы:
```
backend/app/models/
├── __init__.py
├── main_db.py
└── bot_db.py

scripts/
└── create_admin.py
```

---

## ЭТАП 3: Backend API — Auth
**Статус:** ⬜ Не начат

### Задачи:
- [ ] backend/app/utils/__init__.py
- [ ] backend/app/utils/security.py (hash_password, verify_password, create_token, decode_token)
- [ ] backend/app/schemas/__init__.py
- [ ] backend/app/schemas/auth.py (LoginRequest, TokenResponse, AdminResponse)
- [ ] backend/app/api/__init__.py
- [ ] backend/app/api/deps.py (get_db, get_current_admin)
- [ ] backend/app/api/auth.py (login, me)
- [ ] Подключить роутер в main.py

### Эндпоинты:
- [ ] POST /api/auth/login → {"access_token": "..."}
- [ ] GET /api/auth/me → {"id": 1, "username": "admin"}

### Проверка:
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
# → {"access_token": "eyJ..."}

curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer eyJ..."
# → {"id": 1, "username": "admin"}
```

---

## ЭТАП 4: Backend API — CRUD ботов
**Статус:** ⬜ Не начат

### Задачи:
- [ ] backend/app/schemas/bot.py (BotCreate, BotUpdate, BotResponse)
- [ ] backend/app/api/bots.py
- [ ] При создании бота — создавать папку data/bots/{uuid}/ и bot.db
- [ ] При удалении бота — удалять папку

### Эндпоинты:
- [ ] GET /api/bots — список ботов
- [ ] POST /api/bots — создать бота
- [ ] GET /api/bots/{uuid} — получить бота
- [ ] PUT /api/bots/{uuid} — обновить
- [ ] DELETE /api/bots/{uuid} — удалить
- [ ] POST /api/bots/{uuid}/start — запустить (заглушка)
- [ ] POST /api/bots/{uuid}/stop — остановить (заглушка)

### Проверка:
```bash
# Создать бота
curl -X POST http://localhost:8000/api/bots \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Bot", "bot_token": "123:ABC"}'
# → {"uuid": "abc-123", "name": "Test Bot", ...}

# Проверить что создалась папка
ls data/bots/
# → abc-123/

ls data/bots/abc-123/
# → bot.db
```

---

## ЭТАП 5: Backend API — Каналы и тарифы
**Статус:** ⬜ Не начат

### Задачи:
- [ ] backend/app/schemas/channel.py
- [ ] backend/app/schemas/tariff.py
- [ ] backend/app/api/channels.py (работа с bot.db)
- [ ] backend/app/api/tariffs.py

### Эндпоинты каналов:
- [ ] GET /api/bots/{uuid}/channels
- [ ] POST /api/bots/{uuid}/channels
- [ ] GET /api/bots/{uuid}/channels/{id}
- [ ] PUT /api/bots/{uuid}/channels/{id}
- [ ] DELETE /api/bots/{uuid}/channels/{id}

### Эндпоинты тарифов:
- [ ] GET /api/bots/{uuid}/channels/{channel_id}/tariffs
- [ ] POST /api/bots/{uuid}/channels/{channel_id}/tariffs
- [ ] PUT /api/bots/{uuid}/tariffs/{id}
- [ ] DELETE /api/bots/{uuid}/tariffs/{id}

---

## ЭТАП 6: Backend API — Промокоды
**Статус:** ⬜ Не начат

### Задачи:
- [ ] backend/app/schemas/promocode.py
- [ ] backend/app/api/promocodes.py
- [ ] Валидация: срок, лимит, активность

### Эндпоинты:
- [ ] GET /api/bots/{uuid}/promocodes
- [ ] POST /api/bots/{uuid}/promocodes
- [ ] PUT /api/bots/{uuid}/promocodes/{id}
- [ ] DELETE /api/bots/{uuid}/promocodes/{id}
- [ ] POST /api/bots/{uuid}/promocodes/validate — проверить код

---

## ЭТАП 7: Backend API — Рассылки
**Статус:** ⬜ Не начат

### Задачи:
- [ ] backend/app/schemas/broadcast.py
- [ ] backend/app/api/broadcasts.py
- [ ] backend/app/services/__init__.py
- [ ] backend/app/services/broadcast_worker.py (фоновая задача)

### Эндпоинты:
- [ ] GET /api/bots/{uuid}/broadcasts
- [ ] POST /api/bots/{uuid}/broadcasts
- [ ] GET /api/bots/{uuid}/broadcasts/{id}
- [ ] POST /api/bots/{uuid}/broadcasts/{id}/start
- [ ] POST /api/bots/{uuid}/broadcasts/{id}/cancel

---

## ЭТАП 8: Шаблон бота — Ядро
**Статус:** ⬜ Не начат

### Задачи:
- [ ] backend/bot_template/__init__.py
- [ ] backend/bot_template/run.py (точка входа: `python run.py --bot-uuid=xxx`)
- [ ] backend/bot_template/loader.py (Bot, Dispatcher)
- [ ] backend/bot_template/config.py (загрузка конфига из main.db)
- [ ] backend/bot_template/database.py (подключение к bot.db)
- [ ] backend/bot_template/handlers/__init__.py
- [ ] backend/bot_template/handlers/start.py
- [ ] backend/bot_template/handlers/menu.py
- [ ] backend/bot_template/handlers/channels.py
- [ ] backend/bot_template/handlers/tariffs.py
- [ ] backend/bot_template/keyboards/__init__.py
- [ ] backend/bot_template/keyboards/inline.py
- [ ] backend/bot_template/keyboards/reply.py

### Функционал:
- [ ] /start → приветствие + меню
- [ ] Кнопка "Каналы" → список каналов
- [ ] Выбор канала → тарифы
- [ ] Выбор тарифа → кнопка "Оплатить" (заглушка)

### Проверка:
```bash
python backend/bot_template/run.py --bot-uuid=abc-123
# Бот запускается, /start работает
```

---

## ЭТАП 9: Шаблон бота — CryptoBot оплата
**Статус:** ⬜ Не начат

### Задачи:
- [ ] backend/app/services/cryptobot.py (CryptoBot API client)
- [ ] backend/bot_template/handlers/payment.py
- [ ] backend/bot_template/callbacks/__init__.py
- [ ] backend/bot_template/callbacks/payment.py
- [ ] backend/app/api/webhooks.py (webhook от CryptoBot)

### Функционал:
- [ ] Создание инвойса (createInvoice)
- [ ] Отправка кнопки оплаты юзеру
- [ ] Приём webhook при оплате
- [ ] Обновление статуса в БД
- [ ] Уведомление юзера

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

### Функционал:
- [ ] Pyrogram client с session_string
- [ ] Получение задачи "добавить юзера X в канал Y"
- [ ] Добавление юзера
- [ ] Обработка ошибок (FloodWait, UserPrivacyRestricted)

---

## ЭТАП 11: Подписки — Проверка и автокик
**Статус:** ⬜ Не начат

### Задачи:
- [ ] backend/app/services/subscription_checker.py
- [ ] userbot/actions/kick.py
- [ ] Фоновая задача (asyncio loop или APScheduler)

### Функционал:
- [ ] Проверка каждые 5 минут
- [ ] За 1 день до истечения → уведомление
- [ ] При истечении → кик через userbot
- [ ] Обновление is_active = 0, auto_kicked = 1

---

## ЭТАП 12: Шаблон бота — Промокоды и рассылки
**Статус:** ⬜ Не начат

### Задачи:
- [ ] backend/bot_template/handlers/promocode.py
- [ ] backend/bot_template/handlers/subscription.py
- [ ] backend/bot_template/handlers/support.py
- [ ] Интеграция промокода в оплату

### Функционал:
- [ ] Кнопка "Ввести промокод" перед оплатой
- [ ] Применение скидки
- [ ] Кнопка "Мои подписки"
- [ ] Кнопка "Поддержка"

---

## ЭТАП 13: Оркестратор ботов
**Статус:** ⬜ Не начат

### Задачи:
- [ ] backend/app/services/bot_manager.py
- [ ] Запуск бота как subprocess
- [ ] Сохранение PID в main.db
- [ ] Остановка по PID
- [ ] Автозапуск активных ботов при старте backend

### Функционал:
- [ ] start_bot(uuid) → запускает процесс
- [ ] stop_bot(uuid) → останавливает
- [ ] restart_bot(uuid)
- [ ] get_status(uuid) → running/stopped
- [ ] startup_event → запуск всех is_active=1

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
- [ ] frontend/src/pages/Bots/*
- [ ] frontend/src/pages/Channels/*
- [ ] frontend/src/pages/Tariffs/*
- [ ] frontend/src/pages/Promocodes/*
- [ ] frontend/src/pages/Broadcasts/*
- [ ] frontend/src/components/Layout.jsx
- [ ] frontend/src/components/Sidebar.jsx

### Страницы:
- [ ] Login — форма входа
- [ ] Dashboard — статистика
- [ ] Bots — список, создание, редактирование
- [ ] Channels — каналы бота
- [ ] Tariffs — тарифы
- [ ] Promocodes — промокоды
- [ ] Broadcasts — рассылки

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

**Легенда:** ⬜ Не начат | 🔄 В работе | ✅ Готов
