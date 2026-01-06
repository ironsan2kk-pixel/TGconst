# ✅ ЧЕК-ЛИСТ: Telegram-бот продажи доступа к каналам

**Версия:** 4.0  
**Платформа:** Windows Server  
**Архитектура:** Один бот, SQLite, RU/EN

---

## 📋 КАК РАБОТАЕМ

```
1. Ты пишешь: "Чат 1"
2. Я делаю ВСЁ из чата 1
3. Выгружаю в GitHub репо
4. Пишу "проверим"
5. Ты проверяешь, пишешь "проверка"
6. Я проверяю работоспособность
7. Обновляю этот CHECKLIST.md в репо
8. Переходим к "Чат 2"
```

---

## ЧАТ 1: Структура и база данных
**Статус:** ⬜ Не начат

### Конфигурационные файлы:
- [ ] `.gitignore`
```
data/
venv/
__pycache__/
*.pyc
.env
logs/
node_modules/
dist/
.vite/
```
- [ ] `.env.example` (все переменные)
- [ ] `requirements.txt`
- [ ] `README.md` (краткая инструкция)

### Структура папок:
```
- [ ] data/
- [ ] data/backups/
- [ ] data/logs/
- [ ] bot/
- [ ] bot/models/
- [ ] bot/handlers/
- [ ] bot/keyboards/
- [ ] bot/callbacks/
- [ ] bot/middlewares/
- [ ] bot/services/
- [ ] bot/utils/
- [ ] bot/locales/
- [ ] userbot/
- [ ] userbot/actions/
- [ ] admin/
- [ ] admin/api/
- [ ] admin/schemas/
- [ ] admin/utils/
- [ ] frontend/
- [ ] frontend/src/
- [ ] scripts/
```

### SQLAlchemy модели (`bot/models/`):
- [ ] `__init__.py` — экспорт всех моделей
- [ ] `base.py` — Base, async engine, async session
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
- [ ] `bot/database.py` — get_session, init_db
- [ ] Функция создания всех таблиц
- [ ] Функция seed начальных настроек

### Базовый Backend:
- [ ] `admin/__init__.py`
- [ ] `admin/run.py` — точка входа uvicorn
- [ ] `admin/config.py` — Settings из .env
- [ ] `admin/database.py` — подключение к БД
- [ ] `admin/api/__init__.py` — главный роутер
- [ ] `GET /health` → `{"status": "ok"}`

### Windows .bat файлы (UTF-8):
- [ ] `scripts/install.bat` — создание venv, установка зависимостей
- [ ] `scripts/setup_db.bat` — инициализация БД
- [ ] `scripts/start_admin.bat` — запуск FastAPI
- [ ] `scripts/start_bot.bat` — заглушка
- [ ] `scripts/start_all.bat` — запуск всего
- [ ] `scripts/stop_all.bat` — остановка

### Проверка:
```cmd
:: Установка
scripts\install.bat

:: Инициализация БД
scripts\setup_db.bat
:: → Создан data/bot.db

:: Проверка таблиц
sqlite3 data/bot.db ".tables"
:: → settings channels tariffs tariff_channels users subscriptions ...

:: Запуск API
scripts\start_admin.bat
:: http://localhost:8000/health → {"status": "ok"}
```

---

## ЧАТ 2: Telegram бот — Ядро
**Статус:** ⬜ Не начат

### Конфигурация бота:
- [ ] `bot/__init__.py`
- [ ] `bot/config.py` — загрузка из .env и БД
- [ ] `bot/loader.py` — Bot, Dispatcher
- [ ] `bot/run.py` — точка входа

### Локализация:
- [ ] `bot/locales/__init__.py` — функция `t(key, lang, **kwargs)`
- [ ] `bot/locales/ru.py` — все тексты RU
- [ ] `bot/locales/en.py` — все тексты EN

Ключи локализации:
```
welcome, choose_language, language_changed
main_menu, btn_tariffs, btn_my_subs, btn_promocode
btn_language, btn_support
tariffs_title, tariff_details, tariff_channels
btn_buy, btn_back, btn_trial
price_label, duration_days, duration_forever
no_tariffs, no_subscriptions
admin_only, user_banned
new_user_notification, purchase_notification
```

### Middleware:
- [ ] `bot/middlewares/__init__.py`
- [ ] `bot/middlewares/database.py` — сессия в каждый запрос
- [ ] `bot/middlewares/user.py` — регистрация/обновление юзера
- [ ] `bot/middlewares/i18n.py` — определение языка
- [ ] `bot/middlewares/ban.py` — проверка бана

### Клавиатуры:
- [ ] `bot/keyboards/__init__.py`
- [ ] `bot/keyboards/inline.py`:
  - `language_keyboard()`
  - `main_menu_keyboard(lang, custom_buttons)`
  - `tariffs_keyboard(tariffs, lang)`
  - `tariff_detail_keyboard(tariff, lang, has_trial)`
  - `back_keyboard(callback, lang)`
- [ ] `bot/keyboards/reply.py`

### Handlers:
- [ ] `bot/handlers/__init__.py` — регистрация всех роутеров
- [ ] `bot/handlers/start.py`:
  - `/start` — приветствие, выбор языка
  - `/start tariff_{id}` — deep link на тариф
  - `/start ref_{source}` — сохранение UTM
- [ ] `bot/handlers/menu.py`:
  - Показ главного меню
  - `/menu` команда
- [ ] `bot/handlers/tariffs.py`:
  - Список тарифов
  - Детали тарифа (каналы в пакете)
- [ ] `bot/handlers/language.py`:
  - `/language` — смена языка
  - Callback смены языка

### Callbacks:
- [ ] `bot/callbacks/__init__.py`
- [ ] `bot/callbacks/language.py` — `lang:{code}`
- [ ] `bot/callbacks/tariff.py` — `tariff:{id}`, `back:tariffs`

### Сервисы:
- [ ] `bot/services/__init__.py`
- [ ] `bot/services/notifications.py`:
  - `notify_admins(text)` — отправка всем админам
  - Уведомление о новом юзере

### Обновление .bat:
- [ ] `scripts/start_bot.bat` — реальный запуск бота

### Проверка:
```cmd
:: Добавить BOT_TOKEN в .env
:: Запуск бота
scripts\start_bot.bat

:: В Telegram:
:: /start → выбор языка → меню
:: Кнопка "Тарифы" → список
:: Deep link: ?start=tariff_1 → детали тарифа
```

---

## ЧАТ 3: CryptoBot оплата
**Статус:** ⬜ Не начат

### CryptoBot API:
- [ ] `bot/services/cryptobot.py`:
  - `CryptoBotAPI` класс
  - `create_invoice(amount, description, payload)`
  - `get_invoice(invoice_id)`
  - `verify_webhook(body, signature)`

### Handlers оплаты:
- [ ] `bot/handlers/payment.py`:
  - Создание инвойса
  - Отправка кнопки оплаты
  - Проверка статуса (polling fallback)

### Callbacks:
- [ ] `bot/callbacks/payment.py`:
  - `pay:{tariff_id}` — начать оплату
  - `pay:{tariff_id}:{promo_id}` — с промокодом
  - `check:{payment_id}` — проверить статус

### Webhook:
- [ ] `admin/api/webhooks.py`:
  - `POST /webhooks/cryptobot`
  - Проверка подписи
  - Обновление статуса платежа
  - Создание подписки
  - Уведомления

### Сервис подписок:
- [ ] `bot/services/subscription.py`:
  - `create_subscription(user_id, tariff_id, payment_id)`
  - `get_user_subscriptions(user_id)`
  - `get_tariff_channels(tariff_id)`

### Проверка:
```
:: Добавить CRYPTOBOT_TOKEN в .env
:: В боте: выбрать тариф → "Оплатить"
:: Получить ссылку на CryptoBot
:: После оплаты → подписка создана
```

---

## ЧАТ 4: Userbot
**Статус:** ⬜ Не начат

### Конфигурация:
- [ ] `userbot/__init__.py`
- [ ] `userbot/config.py` — API_ID, API_HASH, SESSION
- [ ] `userbot/client.py` — Pyrogram Client singleton

### Действия:
- [ ] `userbot/actions/__init__.py`
- [ ] `userbot/actions/invite.py`:
  - `invite_user(user_id, channel_id)`
  - `invite_to_channels(user_id, channel_ids)`
  - Обработка FloodWait
  - Обработка UserPrivacyRestricted
- [ ] `userbot/actions/kick.py`:
  - `kick_user(user_id, channel_id)`
  - `kick_from_channels(user_id, channel_ids)`

### Точка входа:
- [ ] `userbot/run.py` — запуск клиента

### Интеграция:
- [ ] Вызов `invite_to_channels` после оплаты
- [ ] Логирование результатов

### .bat файлы:
- [ ] `scripts/start_userbot.bat`
- [ ] `scripts/generate_session.bat` — получение session_string

### Проверка:
```cmd
:: Настроить USERBOT_* в .env
:: Сгенерировать session_string
scripts\generate_session.bat

:: Запуск userbot
scripts\start_userbot.bat

:: После оплаты → юзер добавлен в каналы
```

---

## ЧАТ 5: Подписки и напоминания
**Статус:** ⬜ Не начат

### Checker подписок:
- [ ] `bot/services/subscription_checker.py`:
  - `check_expiring_subscriptions()` — найти истекающие
  - `process_expired_subscriptions()` — обработать истёкшие
  - `run_checker()` — asyncio loop

### Напоминания:
- [ ] `bot/services/reminder.py`:
  - `send_reminder_3_days(user_id, subscription)`
  - `send_reminder_1_day(user_id, subscription)`
  - Обновление флагов reminded_*

### Аналитика:
- [ ] `bot/services/analytics.py`:
  - `update_daily_stats()` — обновить статистику за день
  - `get_stats_range(start_date, end_date)`

### Фоновые задачи:
- [ ] Интеграция в `bot/run.py`:
  - Checker каждые 5 минут
  - Напоминания каждые 30 минут
  - Аналитика каждый час

### Проверка:
```
:: Создать подписку с коротким сроком
:: Подождать → получить напоминание
:: После истечения → юзер кикнут
```

---

## ЧАТ 6: Фичи бота
**Статус:** ⬜ Не начат

### Промокоды:
- [ ] `bot/handlers/promocode.py`:
  - Кнопка "Ввести промокод"
  - Валидация и применение
- [ ] `bot/services/promocode.py`:
  - `validate_promocode(code, tariff_id, user_id)`
  - `apply_promocode(code, user_id, payment_id)`
  - `calculate_discount(code, amount)`

### Мои подписки:
- [ ] `bot/handlers/subscription.py`:
  - Список активных подписок
  - Детали: до какого числа, какие каналы
  - История покупок

### Кастомные кнопки:
- [ ] `bot/handlers/custom_buttons.py`:
  - Загрузка из БД
  - Обработка нажатий (URL → открыть, text → показать)

### Админ в боте:
- [ ] `bot/handlers/admin.py`:
  - `/admin` — меню админа
  - `/stats` — быстрая статистика
  - Поиск юзера
  - Выдача доступа
  - Отзыв доступа
  - Бан/разбан
  - **Ручное подтверждение оплаты**

### Callbacks админа:
- [ ] `bot/callbacks/admin.py`:
  - `admin:stats`
  - `admin:find_user`
  - `admin:grant:{user_id}`
  - `admin:revoke:{user_id}:{sub_id}`
  - `admin:ban:{user_id}`
  - `admin:confirm_payment:{payment_id}`

### Пробный период:
- [ ] Кнопка "Попробовать бесплатно" в тарифе
- [ ] Проверка: не брал ли уже trial
- [ ] Создание подписки с `is_trial=1`

### Проверка:
```
:: Промокоды: ввести → скидка применена
:: Мои подписки: список с деталями
:: /admin → меню работает
:: Выдать доступ → юзер добавлен
```

---

## ЧАТ 7: Рассылки
**Статус:** ⬜ Не начат

### Сервис рассылок:
- [ ] `bot/services/broadcast.py`:
  - `create_broadcast(data)` — создать
  - `get_recipients(filter_type, language)` — получатели
  - `start_broadcast(broadcast_id)` — запустить
  - `pause_broadcast(broadcast_id)`
  - `cancel_broadcast(broadcast_id)`
  - `send_message(user_id, broadcast)` — отправить одному

### Фоновая отправка:
- [ ] Asyncio task
- [ ] Обновление прогресса
- [ ] Rate limiting (30 msg/sec)
- [ ] Обработка ошибок

### API рассылок:
- [ ] `admin/api/broadcasts.py`:
  - `GET /broadcasts` — список
  - `POST /broadcasts` — создать
  - `GET /broadcasts/{id}` — детали
  - `POST /broadcasts/{id}/start`
  - `POST /broadcasts/{id}/pause`
  - `POST /broadcasts/{id}/cancel`

### Schemas:
- [ ] `admin/schemas/broadcast.py`

### Проверка:
```
:: Создать рассылку через API
:: Запустить → сообщения отправляются
:: Проверить прогресс
:: Пауза/отмена работают
```

---

## ЧАТ 8: Админка Frontend
**Статус:** ⬜ Не начат

### Backend API (полный):

#### Auth:
- [ ] `admin/api/auth.py`:
  - `POST /auth/login` → JWT
  - `GET /auth/me`
- [ ] `admin/api/deps.py` — get_current_admin
- [ ] `admin/utils/security.py` — JWT, пароли

#### Dashboard & Analytics:
- [ ] `admin/api/dashboard.py`:
  - `GET /dashboard/stats` — карточки
  - `GET /dashboard/chart` — данные графика
  - `GET /dashboard/recent` — последние события
- [ ] `admin/api/analytics.py`:
  - `GET /analytics/revenue` — доход по периодам
  - `GET /analytics/users` — юзеры по периодам
  - `GET /analytics/conversion` — воронка

#### CRUD:
- [ ] `admin/api/channels.py`
- [ ] `admin/api/tariffs.py` (+ управление каналами в тарифе)
- [ ] `admin/api/users.py`:
  - CRUD + grant/revoke/ban/unban
- [ ] `admin/api/subscriptions.py`
- [ ] `admin/api/payments.py`:
  - CRUD + **manual confirm**
  - `POST /payments/{id}/confirm` — ручное подтверждение
  - `POST /payments/manual` — создать ручной платёж
- [ ] `admin/api/promocodes.py`
- [ ] `admin/api/buttons.py`
- [ ] `admin/api/settings.py`

#### Schemas:
- [ ] Все schemas для каждого API

### Frontend React:

#### Базовая структура:
- [ ] `frontend/package.json`
- [ ] `frontend/vite.config.js`
- [ ] `frontend/tailwind.config.js` — dark mode
- [ ] `frontend/index.html`
- [ ] `frontend/src/main.jsx`
- [ ] `frontend/src/App.jsx`
- [ ] `frontend/src/index.css` — dark mode стили

#### Тёмная тема:
- [ ] `frontend/src/ThemeContext.jsx` — контекст темы
- [ ] `frontend/src/components/ThemeToggle.jsx` — переключатель
- [ ] Все компоненты с `dark:` классами

#### API клиент:
- [ ] `frontend/src/api/client.js`
- [ ] `frontend/src/api/auth.js`
- [ ] `frontend/src/api/dashboard.js`
- [ ] `frontend/src/api/analytics.js`
- [ ] `frontend/src/api/channels.js`
- [ ] `frontend/src/api/tariffs.js`
- [ ] `frontend/src/api/users.js`
- [ ] `frontend/src/api/subscriptions.js`
- [ ] `frontend/src/api/payments.js`
- [ ] `frontend/src/api/promocodes.js`
- [ ] `frontend/src/api/broadcasts.js`
- [ ] `frontend/src/api/buttons.js`
- [ ] `frontend/src/api/settings.js`

#### Компоненты:
- [ ] `Layout.jsx` — с sidebar и header
- [ ] `Sidebar.jsx` — навигация
- [ ] `Header.jsx` — с ThemeToggle
- [ ] `StatsCard.jsx`
- [ ] `DataTable.jsx` — с пагинацией и поиском
- [ ] `Modal.jsx`
- [ ] `ConfirmDialog.jsx`
- [ ] `Charts/RevenueChart.jsx` — Recharts
- [ ] `Charts/UsersChart.jsx`
- [ ] `Charts/ConversionChart.jsx`

#### Страницы:
- [ ] `Login.jsx`
- [ ] `Dashboard.jsx` — карточки + графики
- [ ] `Analytics.jsx` — детальная аналитика
- [ ] `Channels/List.jsx`, `Channels/Form.jsx`
- [ ] `Tariffs/List.jsx`, `Tariffs/Form.jsx` — с выбором каналов
- [ ] `Users/List.jsx`, `Users/Detail.jsx` — с действиями
- [ ] `Subscriptions/List.jsx`
- [ ] `Payments/List.jsx` — с кнопкой "Подтвердить"
- [ ] `Payments/ManualForm.jsx` — создание ручного платежа
- [ ] `Promocodes/List.jsx`, `Promocodes/Form.jsx`
- [ ] `Broadcasts/List.jsx`, `Broadcasts/Form.jsx`, `Broadcasts/View.jsx`
- [ ] `Buttons/List.jsx`, `Buttons/Form.jsx`
- [ ] `Settings.jsx`

#### .bat файлы:
- [ ] `scripts/start_frontend.bat`
- [ ] `scripts/build_frontend.bat`

### Проверка:
```cmd
:: Backend
scripts\start_admin.bat
:: http://localhost:8000/docs → Swagger

:: Frontend
cd frontend
npm install
npm run dev
:: http://localhost:3000

:: Проверить:
:: - Логин работает
:: - Dashboard с графиками
:: - Тёмная тема переключается
:: - Все CRUD работают
:: - Ручное подтверждение платежа
```

---

## 📊 ПРОГРЕСС

| # | Чат | Статус | Описание |
|---|-----|--------|----------|
| 1 | Структура и БД | ⬜ | Папки, модели, .bat файлы |
| 2 | Бот — Ядро | ⬜ | /start, меню, тарифы, i18n |
| 3 | CryptoBot | ⬜ | Оплата, webhook |
| 4 | Userbot | ⬜ | Invite/kick |
| 5 | Подписки | ⬜ | Checker, напоминания |
| 6 | Фичи бота | ⬜ | Промокоды, админ, ручная оплата |
| 7 | Рассылки | ⬜ | Broadcast система |
| 8 | Админка | ⬜ | React + тёмная тема + графики |

**Легенда:** ⬜ Не начат | 🔄 В работе | ✅ Готово

---

## 🚀 СТАРТ

1. Напиши **"Чат 1"**
2. Я делаю всё из списка
3. Выгружаю в GitHub
4. Пишу **"проверим"**
5. Ты проверяешь, пишешь **"проверка"**
6. Я проверяю и обновляю чек-лист
7. Переходим к **"Чат 2"**

---

**Готов. Жду команду "Чат 1"!**
