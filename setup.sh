#!/bin/bash

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "Python3 не установлен. Установите Python3."
    exit 1
fi

# Создание виртуального окружения
echo "Создание виртуального окружения..."
python3 -m venv venv

# Активация виртуального окружения
source venv/bin/activate

# Установка Python-зависимостей
echo "Установка Python-зависимостей..."
pip install -r requirements.txt

# Установка Node.js-зависимостей
echo "Установка Node.js-зависимостей..."
cd frontend
npm install
cd ..

# Создание базы данных и применение миграций
echo "Создание базы данных..."
python backend/manage.py migrate

echo "Настройка завершена! Для запуска:"
echo "1. Активируйте окружение: source venv/bin/activate"
echo "2. Запустите Django: python manage.py runserver"
echo "3. Запустите Vue: cd frontend && npm run dev"
