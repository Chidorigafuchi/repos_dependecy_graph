#!/bin/sh
set -eu

echo "Выполняем миграции..."
python manage.py migrate

echo "Добавляем пути к репозиториям..."
python manage.py add_repo_paths

echo "Создаём периодические задачи..."
python manage.py create_periodic_parse_update

echo "Парсим репозитории..."
python manage.py parse_repos

echo "Запускаем Django..."
exec python manage.py runserver 0.0.0.0:8000