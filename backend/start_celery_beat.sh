#!/bin/sh
set -eu

echo "Ожидание завершения миграций..."
until python manage.py showmigrations repos_dependency_graph | grep '\[X\]' > /dev/null; do
  echo "Миграции ещё не завершены, ждём..."
  sleep 2
done

echo "Миграции завершены, запускаем Celery Beat..."
exec celery -A repos_dependency_graph beat --loglevel=info