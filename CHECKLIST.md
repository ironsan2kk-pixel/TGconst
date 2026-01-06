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
- [x] requirements.txt
- [x] .env.example
- [x] backend/run.py
- [x] backend/app/__init__.py
- [x] backend/app/main.py
- [x] backend/app/config.py
- [x] backend/app/database.py
- [x] Создать папку data/

---

## ЭТАП 2: База данных — Модели
**Статус:** ✅ Готово

### Задачи:
- [x] backend/app/models/__init__.py
- [x] backend/app/models/main_db.py
- [x] backend/app/models/bot_db.py
- [x] Функции init_main_db(), init_bot_db()
- [x] Функции get_main_db(), get_bot_db()
- [x] scripts/create_admin.py

---

## ЭТАП 3: Backend API — Auth
**Статус:** ✅ Готово

### Задачи:
- [x] backend/app/utils/security.py
- [x] backend/app/schemas/auth.py
- [x] backend/app/api/deps.py
- [x] backend/app/api/auth.py
- [x] POST /api/auth/login
- [x] GET /api/auth/me

---

## ЭТАП 4: Backend API — CRUD ботов
**Статус:** ✅ Готово

### Задачи:
- [x] backend/app/schemas/bot.py
- [x] backend/app/api/bots.py
- [x] Создание папки и bot.db для каждого бота
- [x] CRUD эндпоинты для ботов

---

## ЭТАП 5: Backend API — Каналы и тарифы
**Статус:** ✅ Готово

### Задачи:
- [x] backend/app/schemas/channel.py
- [x] backend/app/schemas/tariff.py
- [x] backend/app/api/channels.py
- [x] backend/app/api/tariffs.py

---

## ЭТАП 6: Backend API — Промокоды
**Статус:** ✅ Готово

### Задачи:
- [x] backend/app/schemas/promocode.py
- [x] backend/app/api/promocodes.py
- [x] Валидация промокодов

---

## ЭТАП 7: Backend API — Рассылки
**Статус:** ✅ Готово

### Задачи:
- [x] backend/app/schemas/broadcast.py
- [x] backend/app/api/broadcasts.py
- [x] backend/app/services/broadcast_worker.py

---

## ЭТАП 8: Шаблон бота — Ядро
**Статус:** ✅ Готово

### Задачи:
- [x] backend/bot_template/run.py
- [x] backend/bot_template/loader.py
- [x] backend/bot_template/config.py
- [x] backend/bot_template/database.py
- [x] backend/bot_template/handlers/
- [x] backend/bot_template/keyboards/
- [x] /start, меню, каналы, тарифы

---

## ЭТАП 9: Шаблон бота — CryptoBot оплата
**Статус:** ✅ Готово (Проверено)

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
- [x] Ввод промокода перед оплатой

### Эндпоинты webhook:
- POST /api/webhooks/cryptobot/{bot_uuid} - webhook от CryptoBot
- GET /api/webhooks/cryptobot/{bot_uuid}/test - тест соединения

---

## ЭТАП 10: Userbot — Автодобавление
**Статус:** ✅ Готово

### Задачи:
- [x] userbot/__init__.py
- [x] userbot/run.py (FastAPI сервер для задач)
- [x] userbot/config.py
- [x] userbot/client.py (Pyrogram Client)
- [x] userbot/actions/__init__.py
- [x] userbot/actions/invite.py
- [x] userbot/actions/kick.py
- [x] backend/app/services/userbot.py (клиент для взаимодействия с userbot API)
- [x] Обновление backend/app/api/webhooks.py (интеграция с userbot)
- [x] scripts/generate_session.py (генерация session_string)
- [x] scripts/start_userbot.sh
- [x] scripts/supervisor/userbot.conf

### Функционал:
- [x] Pyrogram клиент с session_string
- [x] HTTP API для получения задач (FastAPI на порту 8001)
- [x] Добавление пользователя в канал (POST /invite)
- [x] Удаление пользователя из канала (POST /kick)
- [x] Проверка участия в канале (GET /check/{channel_id}/{user_id})
- [x] Обработка ошибок (FloodWait, UserPrivacyRestricted, и др.)
- [x] Повторные попытки при FloodWait

### Эндпоинты userbot API (порт 8001):
- GET /health - проверка состояния
- POST /invite - добавить пользователя (асинхронно)
- POST /invite/sync - добавить пользователя (синхронно)
- POST /kick - удалить пользователя (асинхронно)
- POST /kick/sync - удалить пользователя (синхронно)
- POST /reconnect - переподключить userbot
- GET /channel/{channel_id} - информация о канале
- GET /check/{channel_id}/{user_id} - проверка участия

### Проверка:
```bash
# Запуск userbot
cd userbot && python run.py

# Проверка health
curl http://localhost:8001/health
# → {"status":"ok","userbot_connected":true,"userbot_info":{...}}

# Тест добавления (синхронно)
curl -X POST http://localhost:8001/invite/sync \
  -H "Content-Type: application/json" \
  -d '{"bot_uuid":"abc-123","user_telegram_id":123456789,"channel_id":1,"subscription_id":1}'
```

---

## ЭТАП 11: Подписки — Проверка и автокик
**Статус:** ✅ Готово

### Задачи:
- [x] backend/app/services/subscription_checker.py
- [x] userbot/actions/kick.py (уже был реализован в Этапе 10)
- [x] Фоновая задача проверки подписок (каждые 5 минут)
- [x] Уведомление пользователей за 1 день до истечения
- [x] Автокик через userbot при истечении подписки
- [x] Обновление статусов is_active=0, auto_kicked=1
- [x] API эндпоинты для ручной проверки и статуса

### Функционал:
- Проверка каждые 5 минут всех активных ботов
- За 1 день до истечения → уведомление в Telegram
- При истечении → кик через userbot + уведомление
- Обновление is_active = 0, auto_kicked = 1

### API эндпоинты:
- POST /api/bots/subscriptions/check - немедленная проверка всех подписок
- GET /api/bots/subscriptions/checker-status - статус фоновой задачи

### Проверка:
```bash
# Статус проверки подписок
curl http://localhost:8000/api/bots/subscriptions/checker-status \
  -H "Authorization: Bearer $TOKEN"
# → {"is_running": true, "check_interval_seconds": 300, "notify_before_days": 1}

# Ручная проверка
curl -X POST http://localhost:8000/api/bots/subscriptions/check \
  -H "Authorization: Bearer $TOKEN"
# → {"success": true, "message": "Проверка завершена", "result": {...}}
```

---

## ЭТАП 12: Шаблон бота — Промокоды и рассылки
**Статус:** ✅ Готово

### Задачи:
- [x] backend/bot_template/handlers/promocode.py
- [x] backend/bot_template/handlers/subscription.py
- [x] backend/bot_template/handlers/support.py
- [x] Интеграция промокодов в оплату
- [x] Обновление handlers/__init__.py

### Функционал:
- [x] Кнопка "🎁 Промокод" в главном меню → ввод/проверка/удаление промокода
- [x] Автоматическое применение скидки при оплате
- [x] Кнопка "📋 Мои подписки" → список подписок с детализацией
- [x] Продление подписки из списка подписок
- [x] Отображение времени до истечения
- [x] Кнопка "💬 Поддержка" → FAQ, информация об аккаунте, контакт поддержки
- [x] FAQ с типовыми вопросами и ответами

### Новые файлы:
```
backend/bot_template/handlers/
├── promocode.py      # Работа с промокодами
├── subscription.py   # Управление подписками
└── support.py        # Поддержка и FAQ
```

### Проверка:
```bash
# В боте:
# 1. Нажать "🎁 Промокод" → ввести код → увидеть скидку
# 2. Выбрать тариф → промокод применяется автоматически
# 3. Нажать "📋 Мои подписки" → увидеть список с таймерами
# 4. Нажать "💬 Поддержка" → FAQ и информация
```

---

## ЭТАП 13: Оркестратор ботов
**Статус:** ✅ Готово

### Задачи:
- [x] backend/app/services/bot_manager.py
- [x] Запуск бота как subprocess
- [x] Сохранение PID в main.db
- [x] Остановка по PID
- [x] Перезапуск бота
- [x] Мониторинг состояния процессов
- [x] Автозапуск активных ботов при старте backend
- [x] Остановка всех ботов при shutdown backend
- [x] Обновление API эндпоинтов (реальная логика вместо заглушек)

### Функционал:
- start_bot(uuid) → запускает процесс, возвращает PID
- stop_bot(uuid) → останавливает процесс по PID
- restart_bot(uuid) → перезапускает бота
- get_status(uuid) → running/stopped + uptime
- autostart_active_bots() → запуск всех is_active=1 при старте
- stop_all_bots() → остановка всех при shutdown

### API эндпоинты:
- POST /api/bots/{uuid}/start - запуск бота (реальный subprocess)
- POST /api/bots/{uuid}/stop - остановка бота (реальный kill)
- POST /api/bots/{uuid}/restart - перезапуск бота
- GET /api/bots/{uuid}/status - статус с PID и uptime
- GET /api/bots/manager/status - статус всех запущенных ботов

### Новые/обновлённые файлы:
```
backend/app/services/
└── bot_manager.py      # Оркестратор ботов (NEW)

backend/app/api/
└── bots.py             # Обновлён: реальная логика вместо заглушек

backend/app/
├── main.py             # Обновлён: автозапуск/остановка ботов
└── database.py         # Обновлён: get_main_session()

backend/app/services/
└── __init__.py         # Обновлён: экспорт BotManager
```

### Проверка:
```bash
# Запуск бота
curl -X POST http://localhost:8000/api/bots/$UUID/start \
  -H "Authorization: Bearer $TOKEN"
# → {"uuid": "...", "is_active": true, "process_pid": 12345, "message": "Бот успешно запущен (PID: 12345)"}

# Статус бота
curl http://localhost:8000/api/bots/$UUID/status \
  -H "Authorization: Bearer $TOKEN"
# → {"uuid": "...", "is_active": true, "process_pid": 12345, "message": "Бот запущен (PID: 12345, uptime: 120s)"}

# Остановка бота
curl -X POST http://localhost:8000/api/bots/$UUID/stop \
  -H "Authorization: Bearer $TOKEN"
# → {"uuid": "...", "is_active": false, "process_pid": null, "message": "Бот остановлен (был PID: 12345)"}

# Перезапуск бота
curl -X POST http://localhost:8000/api/bots/$UUID/restart \
  -H "Authorization: Bearer $TOKEN"
# → {"uuid": "...", "is_active": true, "process_pid": 12346, "message": "Бот успешно перезапущен"}

# Статус всех ботов
curl http://localhost:8000/api/bots/manager/status \
  -H "Authorization: Bearer $TOKEN"
# → {"running_count": 2, "bots": {"uuid1": {...}, "uuid2": {...}}}

# При рестарте backend → активные боты автозапускаются
# При остановке backend → все боты корректно останавливаются
```

---

## ЭТАП 14: Админка — Frontend
**Статус:** ✅ Готово

### Задачи:
- [x] frontend/package.json (React 18.2 + Vite 5.0 + Tailwind CSS 3.4)
- [x] frontend/vite.config.js (proxy /api → localhost:8000)
- [x] frontend/tailwind.config.js (кастомные цвета primary)
- [x] frontend/postcss.config.js
- [x] frontend/index.html
- [x] frontend/src/main.jsx
- [x] frontend/src/App.jsx (роутинг всех страниц)
- [x] frontend/src/index.css (Tailwind directives)

### API клиенты:
- [x] frontend/src/api/client.js (axios с auth interceptors)
- [x] frontend/src/api/auth.js (login, getMe)
- [x] frontend/src/api/bots.js (CRUD + start/stop/restart/status)
- [x] frontend/src/api/channels.js (CRUD)
- [x] frontend/src/api/tariffs.js (CRUD)
- [x] frontend/src/api/promocodes.js (CRUD + validate)
- [x] frontend/src/api/broadcasts.js (CRUD + start/cancel/stats)

### Контекст и хуки:
- [x] frontend/src/context/AuthContext.jsx
- [x] frontend/src/hooks/useAuth.js

### Компоненты:
- [x] frontend/src/components/Layout.jsx
- [x] frontend/src/components/Sidebar.jsx (динамическая навигация)
- [x] frontend/src/components/Header.jsx
- [x] frontend/src/components/ui/Button.jsx (5 вариантов, 3 размера, loading)
- [x] frontend/src/components/ui/Input.jsx (Input, Textarea, Select, Checkbox)
- [x] frontend/src/components/ui/Card.jsx (Card, CardHeader, CardTitle, CardContent, CardFooter)
- [x] frontend/src/components/ui/Badge.jsx (Badge, Alert, Modal, EmptyState, Spinner)

### Страницы:
- [x] frontend/src/pages/Login.jsx
- [x] frontend/src/pages/Dashboard.jsx
- [x] frontend/src/pages/Bots/BotList.jsx
- [x] frontend/src/pages/Bots/BotCreate.jsx
- [x] frontend/src/pages/Bots/BotEdit.jsx
- [x] frontend/src/pages/Channels/ChannelList.jsx
- [x] frontend/src/pages/Channels/ChannelCreate.jsx
- [x] frontend/src/pages/Channels/ChannelEdit.jsx
- [x] frontend/src/pages/Tariffs/TariffList.jsx
- [x] frontend/src/pages/Tariffs/TariffCreate.jsx
- [x] frontend/src/pages/Tariffs/TariffEdit.jsx
- [x] frontend/src/pages/Promocodes/PromocodeList.jsx
- [x] frontend/src/pages/Promocodes/PromocodeCreate.jsx
- [x] frontend/src/pages/Promocodes/PromocodeEdit.jsx
- [x] frontend/src/pages/Broadcasts/BroadcastList.jsx
- [x] frontend/src/pages/Broadcasts/BroadcastCreate.jsx
- [x] frontend/src/pages/Broadcasts/BroadcastView.jsx

### Структура файлов:
```
frontend/
├── package.json
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
├── index.html
└── src/
    ├── main.jsx
    ├── App.jsx
    ├── index.css
    ├── api/
    │   ├── client.js
    │   ├── auth.js
    │   ├── bots.js
    │   ├── channels.js
    │   ├── tariffs.js
    │   ├── promocodes.js
    │   └── broadcasts.js
    ├── context/
    │   └── AuthContext.jsx
    ├── hooks/
    │   └── useAuth.js
    ├── components/
    │   ├── Layout.jsx
    │   ├── Sidebar.jsx
    │   ├── Header.jsx
    │   └── ui/
    │       ├── Button.jsx
    │       ├── Input.jsx
    │       ├── Card.jsx
    │       └── Badge.jsx
    └── pages/
        ├── Login.jsx
        ├── Dashboard.jsx
        ├── Bots/
        │   ├── BotList.jsx
        │   ├── BotCreate.jsx
        │   └── BotEdit.jsx
        ├── Channels/
        │   ├── ChannelList.jsx
        │   ├── ChannelCreate.jsx
        │   └── ChannelEdit.jsx
        ├── Tariffs/
        │   ├── TariffList.jsx
        │   ├── TariffCreate.jsx
        │   └── TariffEdit.jsx
        ├── Promocodes/
        │   ├── PromocodeList.jsx
        │   ├── PromocodeCreate.jsx
        │   └── PromocodeEdit.jsx
        └── Broadcasts/
            ├── BroadcastList.jsx
            ├── BroadcastCreate.jsx
            └── BroadcastView.jsx
```

### Функционал:
- JWT авторизация с автоматическим редиректом на /login при 401
- Динамическая навигация: главное меню или меню бота
- CRUD для ботов с управлением (start/stop/restart)
- CRUD для каналов и тарифов
- CRUD для промокодов с валидацией
- Управление рассылками (создание, запуск, отмена, статистика)
- Модальные окна подтверждения удаления
- Loading states и error handling
- Responsive дизайн

### Проверка:
```bash
cd frontend
npm install
npm run dev
# http://localhost:3000 → логин → дашборд → CRUD работает
```

---

## ЭТАП 15: Деплой и документация
**Статус:** ⬜ Не начат

### Задачи:
- [ ] scripts/install.sh
- [ ] supervisor конфиги
- [ ] nginx.conf
- [ ] README.md

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
| 10 | Userbot — Автодобавление | ✅ |
| 11 | Подписки — Проверка и автокик | ✅ |
| 12 | Шаблон бота — Промокоды и рассылки | ✅ |
| 13 | Оркестратор ботов | ✅ |
| 14 | Админка — Frontend | ✅ |
| 15 | Деплой и документация | ⬜ |

**Легенда:** ⬜ Не начат | ✅ Готово

**Прогресс:** 14/15 этапов (93%)

---

## 🚀 ПРОДОЛЖЕНИЕ

Напиши **"Этап 15"** для продолжения работы.

