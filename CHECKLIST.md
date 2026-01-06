# ✅ ЧЕК-ЛИСТ: Telegram-бот продажи доступа к каналам

**Версия:** 4.0  
**Платформа:** Windows Server  
**Архитектура:** Один бот, SQLite, RU/EN

---

## 📋 КАК РАБОТАЕМ

```
Ты пишешь: "Чат 1" → Я делаю ВСЁ из чата 1
Выгружаю в репо → Ты проверяешь
Пишешь "Чат 2" или замечания → Продолжаем
```

---

## ЧАТ 1: Структура и база данных
**Статус:** ⬜ Не начат

### Задачи:

#### Конфигурационные файлы:
- [ ] `.gitignore`
- [ ] `.env.example`
- [ ] `requirements.txt`
- [ ] `README.md`

#### Структура папок:
- [ ] `data/`
- [ ] `bot/` + подпапки (models, handlers, keyboards, callbacks, middlewares, services, utils, locales)
- [ ] `userbot/` + actions/
- [ ] `admin/` + api/, schemas/, utils/
- [ ] `frontend/`
- [ ] `scripts/`

#### SQLAlchemy модели (bot/models/):
- [ ] `base.py` — Base, async engine
- [ ] `settings.py` — Settings
- [ ] `channel.py` — Channel
- [ ] `tariff.py` — Tariff, TariffChannel
- [ ] `user.py` — User
- [ ] `subscription.py` — Subscription
- [ ] `payment.py` — Payment
- [ ] `promocode.py` — Promocode, PromocodeUse
- [ ] `broadcast.py` — Broadcast
- [ ] `custom_button.py` — CustomButton
- [ ] `admin_log.py` — AdminLog
- [ ] `stats.py` — StatDaily

#### База данных и скрипты:
- [ ] `bot/database.py` — async engine, get_session, init_db()
- [ ] `bot/config.py` — Settings
- [ ] `scripts/setup_db.py`
- [ ] `scripts/install.bat`

#### Базовый Backend:
- [ ] `admin/run.py`
- [ ] `admin/config.py`
- [ ] `admin/database.py`
- [ ] `admin/api/__init__.py`
- [ ] `GET /health`

### Проверка:
```cmd
scripts\install.bat
python scripts\setup_db.py
python admin\run.py
:: http://localhost:8000/health
```

---

## ЧАТ 2: Telegram бот — Ядро
**Статус:** ⬜ Не начат

### Задачи:
- [ ] `bot/locales/` — RU/EN тексты
- [ ] `bot/loader.py` — Bot, Dispatcher
- [ ] `bot/run.py`
- [ ] `bot/middlewares/` — database, user, i18n, throttling
- [ ] `bot/keyboards/inline.py`
- [ ] `bot/handlers/start.py` — /start + deep links
- [ ] `bot/handlers/menu.py`
- [ ] `bot/handlers/tariffs.py`
- [ ] `bot/handlers/language.py`
- [ ] `bot/callbacks/`
- [ ] `bot/services/notifications.py`
- [ ] `scripts/start_bot.bat`

---

## ЧАТ 3: CryptoBot оплата
**Статус:** ⬜ Не начат

### Задачи:
- [ ] `bot/services/cryptobot.py`
- [ ] `bot/handlers/payment.py`
- [ ] `bot/callbacks/payment.py`
- [ ] `admin/api/webhooks.py`
- [ ] `bot/services/subscription.py`

---

## ЧАТ 4: Userbot — Автодобавление
**Статус:** ⬜ Не начат

### Задачи:
- [ ] `userbot/config.py`
- [ ] `userbot/client.py`
- [ ] `userbot/actions/invite.py`
- [ ] `userbot/run.py`
- [ ] `scripts/generate_session.py`
- [ ] `scripts/start_userbot.bat`

---

## ЧАТ 5: Подписки — Проверка и напоминания
**Статус:** ⬜ Не начат

### Задачи:
- [ ] `userbot/actions/kick.py`
- [ ] `bot/services/reminder.py`
- [ ] Расширение subscription.py
- [ ] Фоновые задачи в bot/run.py

---

## ЧАТ 6: Фичи бота — Промокоды, админ
**Статус:** ⬜ Не начат

### Задачи:
- [ ] `bot/handlers/promocode.py`
- [ ] `bot/services/promocode.py`
- [ ] `bot/handlers/subscription.py`
- [ ] `bot/handlers/custom_buttons.py`
- [ ] `bot/handlers/admin.py`
- [ ] `bot/callbacks/admin.py`

---

## ЧАТ 7: Рассылки
**Статус:** ⬜ Не начат

### Задачи:
- [ ] `bot/services/broadcast.py`
- [ ] `admin/api/broadcasts.py`
- [ ] Быстрая рассылка в /admin

---

## ЧАТ 8: Админ-панель (Web)
**Статус:** ⬜ Не начат

### Задачи:

#### Backend API:
- [ ] `admin/api/auth.py`
- [ ] `admin/api/deps.py`
- [ ] `admin/api/dashboard.py`
- [ ] `admin/api/channels.py`
- [ ] `admin/api/tariffs.py`
- [ ] `admin/api/users.py`
- [ ] `admin/api/subscriptions.py`
- [ ] `admin/api/payments.py` (+ confirm)
- [ ] `admin/api/promocodes.py`
- [ ] `admin/api/buttons.py`
- [ ] `admin/api/settings.py`
- [ ] `admin/schemas/`
- [ ] `admin/utils/security.py`

#### Frontend React:
- [ ] `frontend/package.json`
- [ ] `frontend/vite.config.js`
- [ ] `frontend/tailwind.config.js`
- [ ] `ThemeContext.jsx` — тёмная тема
- [ ] `Charts/` — графики Recharts
- [ ] Все страницы (Dashboard, Channels, Tariffs, Users, Payments, etc.)

#### Скрипты:
- [ ] `scripts/start_admin.bat`
- [ ] `scripts/start_frontend.bat`
- [ ] `scripts/start_all.bat`
- [ ] `scripts/stop_all.bat`
- [ ] `scripts/backup_db.bat`

---

## 📊 ПРОГРЕСС

| # | Чат | Статус |
|---|-----|--------|
| 1 | Структура и БД | ⬜ |
| 2 | Бот — Ядро | ⬜ |
| 3 | CryptoBot | ⬜ |
| 4 | Userbot | ⬜ |
| 5 | Подписки | ⬜ |
| 6 | Фичи бота | ⬜ |
| 7 | Рассылки | ⬜ |
| 8 | Админка | ⬜ |

**Легенда:** ⬜ Не начат | 🔄 В работе | ✅ Готово

---

**Напиши "Чат 1" для старта!**
