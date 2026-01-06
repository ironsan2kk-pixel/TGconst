# 🤖 ИНСТРУКЦИЯ ДЛЯ CLAUDE

**Проект:** Telegram-бот продажи доступа к каналам  
**Версия:** 4.0  
**Дата создания:** Январь 2025

---

## 🔐 ДОСТУПЫ

### GitHub Repository
```
URL: https://github.com/ironsan2kk-pixel/TGconst
Token: [ПЕРЕДАЁТСЯ В НАЧАЛЕ КАЖДОГО ЧАТА]
```

**ВАЖНО:** Токен GitHub передаётся пользователем в начале каждого нового чата.
Claude запоминает токен на время сессии и использует для работы с репозиторием.

### Работа с GitHub API
```bash
# Получить содержимое папки
curl -s -H "Authorization: token {TOKEN}" \
  "https://api.github.com/repos/ironsan2kk-pixel/TGconst/contents/{path}"

# Получить файл (raw)
curl -s -H "Authorization: token {TOKEN}" \
  "https://raw.githubusercontent.com/ironsan2kk-pixel/TGconst/main/{path}"

# Создать/обновить файл
curl -X PUT -H "Authorization: token {TOKEN}" \
  -H "Content-Type: application/json" \
  "https://api.github.com/repos/ironsan2kk-pixel/TGconst/contents/{path}" \
  -d '{
    "message": "commit message",
    "content": "base64_encoded_content",
    "sha": "sha_of_existing_file_if_updating"
  }'

# Удалить файл
curl -X DELETE -H "Authorization: token {TOKEN}" \
  -H "Content-Type: application/json" \
  "https://api.github.com/repos/ironsan2kk-pixel/TGconst/contents/{path}" \
  -d '{
    "message": "delete message",
    "sha": "sha_of_file"
  }'
```

---

## 📋 РАБОЧИЙ ПРОЦЕСС

### Цикл работы над чатом:

```
1. Пользователь пишет: "Чат N"

2. Claude:
   - Читает CHECKLIST.md из репо
   - Выполняет ВСЕ задачи из "Чат N"
   - Создаёт файлы локально
   - Выгружает в GitHub репо
   - Делает коммит с сообщением: "Чат N: краткое описание"
   - Пишет пользователю: "проверим"

3. Пользователь проверяет и пишет: "проверка"

4. Claude:
   - Скачивает файлы из репо
   - Проверяет работоспособность (lint, запуск)
   - Если есть ошибки — исправляет
   - Обновляет CHECKLIST.md (меняет ⬜ на ✅)
   - Выгружает обновлённый CHECKLIST.md
   - Сообщает о готовности к следующему чату
```

### Формат коммитов:
```
Чат 1: Структура проекта и база данных
Чат 2: Telegram бот - ядро
Чат 3: CryptoBot интеграция
...
Fix: исправление ошибки в {файл}
Update: обновление {что}
```

---

## 🖥️ ПЛАТФОРМА: Windows Server

### Важные правила для Windows:

1. **Кодировка .bat файлов:**
   - Использовать UTF-8
   - В начале каждого .bat файла: `chcp 65001 >nul`
   - Для русского текста в консоли

2. **Пути:**
   - Использовать `%~dp0` для относительных путей
   - Обратные слеши: `\`
   - Кавычки для путей с пробелами

3. **Python:**
   - Команда: `python` или `py -3`
   - venv: `venv\Scripts\activate`

4. **Шаблон .bat файла:**
```batch
@echo off
chcp 65001 >nul
cd /d "%~dp0.."

:: Описание что делает скрипт

call venv\Scripts\activate
python команда
pause
```

5. **Переносы строк:**
   - Windows: CRLF (`\r\n`)
   - При создании файлов учитывать это

---

## 📁 СТРУКТУРА ПРОЕКТА

```
telegram-channel-bot/
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
├── MASTER_PLAN.md
├── CHECKLIST.md
├── CLAUDE_INSTRUCTION.md          ← ЭТОТ ФАЙЛ
│
├── data/                           # В .gitignore
│   ├── bot.db
│   ├── backups/
│   └── logs/
│
├── bot/                            # Telegram бот (Aiogram 3)
│   ├── run.py
│   ├── loader.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   ├── handlers/
│   ├── keyboards/
│   ├── callbacks/
│   ├── middlewares/
│   ├── services/
│   ├── utils/
│   └── locales/
│
├── userbot/                        # Pyrogram
│   ├── run.py
│   ├── config.py
│   ├── client.py
│   └── actions/
│
├── admin/                          # FastAPI backend
│   ├── run.py
│   ├── config.py
│   ├── database.py
│   ├── api/
│   ├── schemas/
│   └── utils/
│
├── frontend/                       # React + Tailwind
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── src/
│
└── scripts/                        # Windows .bat
    ├── install.bat
    ├── setup_db.bat
    ├── start_bot.bat
    ├── start_admin.bat
    ├── start_userbot.bat
    ├── start_frontend.bat
    ├── start_all.bat
    ├── stop_all.bat
    ├── backup_db.bat
    └── generate_session.bat
```

---

## 🔧 ТЕХНИЧЕСКИЕ ТРЕБОВАНИЯ

### Python зависимости (requirements.txt):
```
# FastAPI & Server
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
python-multipart>=0.0.9

# Database
sqlalchemy[asyncio]>=2.0.25
aiosqlite>=0.19.0

# Telegram
aiogram>=3.3.0
pyrogram>=2.0.106
tgcrypto>=1.2.5

# Validation & Settings
pydantic>=2.6.0
pydantic-settings>=2.1.0

# Auth & Security
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
bcrypt>=4.0.1

# HTTP Client
httpx>=0.26.0

# Utils
python-dotenv>=1.0.1
```

### Frontend зависимости (package.json):
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.22.0",
    "axios": "^1.6.7",
    "recharts": "^2.10.0",
    "lucide-react": "^0.330.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.2.1",
    "vite": "^5.1.0",
    "tailwindcss": "^3.4.1",
    "postcss": "^8.4.35",
    "autoprefixer": "^10.4.17"
  }
}
```

---

## 🗄️ БАЗА ДАННЫХ

### Таблицы:
1. `settings` — настройки (key-value)
2. `channels` — каналы
3. `tariffs` — тарифы (пакеты)
4. `tariff_channels` — связь тариф↔каналы
5. `users` — пользователи
6. `subscriptions` — подписки
7. `payments` — платежи
8. `promocodes` — промокоды
9. `promocode_uses` — использования промокодов
10. `broadcasts` — рассылки
11. `custom_buttons` — кастомные кнопки
12. `admin_logs` — логи админа
13. `analytics_daily` — ежедневная статистика

### SQLAlchemy:
- Использовать async engine
- Mapped columns (SQLAlchemy 2.0 style)
- Relationships с cascade

---

## 🌐 ЛОКАЛИЗАЦИЯ

### Языки: RU, EN

### Структура locales:
```python
# bot/locales/ru.py
TEXTS = {
    "welcome": "👋 Добро пожаловать!",
    "choose_language": "🌐 Выберите язык:",
    # ...
}

# bot/locales/__init__.py
def t(key: str, lang: str = "ru", **kwargs) -> str:
    """Получить перевод"""
    texts = RU_TEXTS if lang == "ru" else EN_TEXTS
    text = texts.get(key, key)
    return text.format(**kwargs) if kwargs else text
```

---

## 🎨 FRONTEND: Тёмная тема

### Tailwind config:
```javascript
// tailwind.config.js
module.exports = {
  darkMode: 'class',
  // ...
}
```

### ThemeContext:
```jsx
// ThemeContext.jsx
const ThemeContext = createContext();

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState(
    localStorage.getItem('theme') || 'light'
  );
  
  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark');
    localStorage.setItem('theme', theme);
  }, [theme]);
  
  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}
```

### Использование в компонентах:
```jsx
<div className="bg-white dark:bg-gray-800 text-gray-900 dark:text-white">
  ...
</div>
```

---

## 📊 ГРАФИКИ (Recharts)

### Пример графика дохода:
```jsx
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

function RevenueChart({ data }) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <XAxis dataKey="date" />
        <YAxis />
        <Tooltip />
        <Line type="monotone" dataKey="amount" stroke="#8884d8" />
      </LineChart>
    </ResponsiveContainer>
  );
}
```

---

## 🔗 DEEP LINKS

### Формат:
```
https://t.me/{bot_username}?start=tariff_{id}
https://t.me/{bot_username}?start=ref_{source}
```

### Обработка в боте:
```python
@router.message(CommandStart(deep_link=True))
async def cmd_start_deep(message: Message, command: CommandObject):
    args = command.args  # "tariff_5" или "ref_google"
    
    if args.startswith("tariff_"):
        tariff_id = int(args.split("_")[1])
        # Показать тариф
    elif args.startswith("ref_"):
        source = args.split("_")[1]
        # Сохранить utm_source
```

---

## 💰 РУЧНОЕ ПОДТВЕРЖДЕНИЕ ОПЛАТЫ

### Флоу:
1. Юзер выбирает тариф, нажимает "Оплатить"
2. Создаётся payment со статусом `pending`
3. Юзер пишет админу "оплатил переводом"
4. Админ в панели:
   - Видит pending платёж
   - Нажимает "Подтвердить"
   - Указывает сумму (опционально)
5. Платёж → `status: manual`, `confirmed_by: admin_id`
6. Создаётся подписка
7. Userbot добавляет в каналы
8. Уведомление юзеру

### API endpoint:
```
POST /payments/{id}/confirm
Body: { "amount": 10.0 }  // опционально
```

---

## ⏰ НАПОМИНАНИЯ

### Настройка:
```
REMINDER_DAYS=3,1  # Напоминать за 3 и 1 день
```

### Логика:
1. Checker запускается каждые 30 минут
2. Находит подписки где `expires_at` через N дней
3. Проверяет флаги `reminded_3_days`, `reminded_1_day`
4. Отправляет сообщение
5. Ставит флаг

### Текст напоминания:
```
🔔 Ваша подписка "{tariff_name}" истекает через {days} дня!

Продлите сейчас, чтобы не потерять доступ.

[Продлить подписку]
```

---

## 📝 ПРАВИЛА НАПИСАНИЯ КОДА

### Python:
- Type hints везде
- Async/await для I/O
- Docstrings для публичных функций
- Pydantic для валидации

### React:
- Functional components + hooks
- Tailwind для стилей
- Axios для API
- Error boundaries

### Общее:
- Понятные имена переменных
- Комментарии на русском (для Alex)
- Логирование важных действий
- Обработка ошибок

---

## 🚨 ВАЖНЫЕ НАПОМИНАНИЯ

1. **Перед началом чата** — прочитать CHECKLIST.md из репо
2. **После выполнения** — всегда выгружать в репо
3. **Коммиты** — понятные сообщения на русском
4. **Windows** — не забывать про кодировку .bat
5. **Тестирование** — проверять что файлы валидны
6. **CHECKLIST** — обновлять статусы после проверки

---

## 🔄 ЧИСТЫЙ СТАРТ

При начале работы нужно:
1. Удалить все старые файлы из репо (кроме .git)
2. Создать новую структуру
3. Выгрузить MASTER_PLAN.md, CHECKLIST.md, CLAUDE_INSTRUCTION.md

---

## 📞 КОНТЕКСТ ПРОЕКТА

**Что делаем:**
- Telegram бот для продажи доступа к приватным каналам
- Оплата через CryptoBot (USDT)
- Один бот, не конструктор
- Пакеты каналов (один тариф = несколько каналов)
- Два языка: RU и EN
- Полная админ-панель с тёмной темой и графиками

**Для кого:**
- Alex — владелец, запускает на Windows Server
- Проверяет работоспособность сам

**Как работаем:**
- По чатам (Чат 1, Чат 2, ...)
- После каждого чата — проверка
- Всё выгружается в GitHub

---

**Готов к работе. Жду команду "Чат 1"!**
