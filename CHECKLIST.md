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
**Статус:** ⬜ Не начат

### Задачи:
- [ ] backend/app/services/subscription_checker.py
- [ ] userbot/actions/kick.py
- [ ] Фоновая задача проверки подписок

---

## ЭТАП 12: Шаблон бота — Промокоды и рассылки
**Статус:** ⬜ Не начат

### Задачи:
- [ ] backend/bot_template/handlers/promocode.py
- [ ] backend/bot_template/handlers/subscription.py
- [ ] backend/bot_template/handlers/support.py

---

## ЭТАП 13: Оркестратор ботов
**Статус:** ⬜ Не начат

### Задачи:
- [ ] backend/app/services/bot_manager.py
- [ ] Запуск/остановка ботов как subprocess
- [ ] Автозапуск активных ботов

---

## ЭТАП 14: Админка — Frontend
**Статус:** ⬜ Не начат

### Задачи:
- [ ] frontend/package.json
- [ ] React + Vite + Tailwind
- [ ] Страницы: Login, Dashboard, Bots, Channels, Tariffs, Promocodes, Broadcasts

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
| 11 | Подписки — Проверка и автокик | ⬜ |
| 12 | Шаблон бота — Промокоды и рассылки | ⬜ |
| 13 | Оркестратор ботов | ⬜ |
| 14 | Админка — Frontend | ⬜ |
| 15 | Деплой и документация | ⬜ |

**Легенда:** ⬜ Не начат | ✅ Готово

**Прогресс:** 10/15 этапов (67%)

---

## 🚀 ПРОДОЛЖЕНИЕ

Напиши **"Этап 11"** для продолжения работы.
