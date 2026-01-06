# ✅ ЧЕК-ЛИСТ: Telegram-бот продажи доступа к каналам

**Версия:** 3.0  
**Платформа:** Windows Server  
**Архитектура:** Один бот, SQLite, RU/EN

---

## 📋 КАК РАБОТАЕМ

```
Ты пишешь: "Чат 1" → Я делаю ВСЁ из чата 1
Я пушу в GitHub → Ты проверяешь
Ты пишешь: "ОК" или замечания
Ты пишешь: "Чат 2" → Я делаю чат 2
... и так до конца
```

---

## ЧАТ 1: Структура и база данных
**Статус:** ⬜ Не начат

### Файлы конфигурации:
- [ ] `.gitignore` (data/, venv/, __pycache__, .env, logs/, node_modules/)
- [ ] `.env.example` (все переменные)
- [ ] `requirements.txt`
- [ ] `README.md`

### Структура папок:
- [ ] data/, data/backups/, data/logs/
- [ ] bot/, bot/models/, bot/handlers/, bot/keyboards/
- [ ] bot/callbacks/, bot/middlewares/, bot/services/
- [ ] bot/utils/, bot/locales/
- [ ] userbot/, userbot/actions/
- [ ] admin/, admin/api/, admin/schemas/, admin/utils/
- [ ] frontend/, frontend/src/
- [ ] scripts/

### SQLAlchemy модели (bot/models/):
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

### База данных:
- [ ] `bot/database.py` — engine, session, init_db()

### Базовый Backend:
- [ ] `admin/run.py`, `admin/config.py`, `admin/database.py`
- [ ] `admin/api/__init__.py`
- [ ] `GET /health` endpoint

### Windows .bat скрипты (UTF-8):
- [ ] `scripts/install.bat`
- [ ] `scripts/setup_db.bat`
- [ ] `scripts/start_bot.bat`
- [ ] `scripts/start_admin.bat`
- [ ] `scripts/start_userbot.bat`
- [ ] `scripts/start_all.bat`
- [ ] `scripts/stop_all.bat`
- [ ] `scripts/backup_db.bat`

---

## ЧАТ 2: Telegram бот — Ядро
**Статус:** ⬜ Не начат

### Локализация:
- [ ] `bot/locales/__init__.py` — t(key, lang)
- [ ] `bot/locales/ru.py`
- [ ] `bot/locales/en.py`

### Конфигурация:
- [ ] `bot/config.py`, `bot/loader.py`

### Middleware:
- [ ] database.py, user.py, i18n.py, ban.py

### Клавиатуры:
- [ ] inline.py — все клавиатуры
- [ ] reply.py

### Handlers:
- [ ] start.py — /start + deep links
- [ ] menu.py — главное меню
- [ ] language.py — смена языка
- [ ] tariffs.py — список и детали

### Callbacks:
- [ ] language.py, tariff.py

### Сервисы:
- [ ] notifications.py — уведомления админам

### Точка входа:
- [ ] `bot/run.py`

---

## ЧАТ 3: CryptoBot оплата
**Статус:** ⬜ Не начат

- [ ] `bot/services/cryptobot.py` — API клиент
- [ ] `bot/handlers/payment.py`
- [ ] `bot/callbacks/payment.py`
- [ ] `bot/services/subscription.py`
- [ ] `admin/api/webhooks.py` — webhook CryptoBot

---

## ЧАТ 4: Userbot + Подписки
**Статус:** ⬜ Не начат

- [ ] `userbot/config.py`, `userbot/client.py`, `userbot/run.py`
- [ ] `userbot/actions/invite.py`, `userbot/actions/kick.py`
- [ ] `bot/services/subscription_checker.py`
- [ ] `bot/services/reminder.py`
- [ ] `scripts/generate_session.bat`

---

## ЧАТ 5: Фичи бота
**Статус:** ⬜ Не начат

- [ ] Промокоды: handlers + services
- [ ] Мои подписки: handler
- [ ] Кастомные кнопки: handler
- [ ] Пробный период
- [ ] /admin панель в боте
- [ ] Ручное подтверждение оплаты

---

## ЧАТ 6: Рассылки
**Статус:** ⬜ Не начат

- [ ] `bot/services/broadcast.py`
- [ ] `admin/api/broadcasts.py`
- [ ] Фильтры получателей
- [ ] Прогресс отправки

---

## ЧАТ 7: Админка Backend
**Статус:** ⬜ Не начат

- [ ] JWT авторизация
- [ ] Dashboard + Analytics endpoints
- [ ] CRUD: channels, tariffs, users, subscriptions
- [ ] Payments с ручным подтверждением
- [ ] Promocodes, broadcasts, buttons, settings

---

## ЧАТ 8: Админка Frontend
**Статус:** ⬜ Не начат

- [ ] React + Tailwind + Recharts
- [ ] Тёмная тема (ThemeContext)
- [ ] Dashboard с графиками
- [ ] Все CRUD страницы
- [ ] Управление юзерами
- [ ] Ручное подтверждение оплат

---

## 📊 ПРОГРЕСС

| # | Чат | Статус |
|---|-----|--------|
| 1 | Структура и БД | ⬜ |
| 2 | Бот — Ядро | ⬜ |
| 3 | CryptoBot | ⬜ |
| 4 | Userbot + Подписки | ⬜ |
| 5 | Фичи бота | ⬜ |
| 6 | Рассылки | ⬜ |
| 7 | Админка Backend | ⬜ |
| 8 | Админка Frontend | ⬜ |

**Легенда:** ⬜ Не начат | 🔄 В работе | ✅ Готово

---

**Готов. Жду "Чат 1"!**
