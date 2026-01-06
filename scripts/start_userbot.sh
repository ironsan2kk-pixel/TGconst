#!/bin/bash
# Скрипт для запуска Userbot

# Определяем директорию проекта
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Активируем виртуальное окружение если есть
if [ -f "$PROJECT_ROOT/venv/bin/activate" ]; then
    source "$PROJECT_ROOT/venv/bin/activate"
fi

# Переходим в директорию userbot
cd "$PROJECT_ROOT/userbot"

# Запускаем
echo "Запуск Userbot..."
python run.py
