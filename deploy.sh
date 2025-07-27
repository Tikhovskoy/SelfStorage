#!/bin/bash

set -e
set -o pipefail

cd "$(dirname "$0")" || exit 1

echo "Обновление проекта SelfStorage"

if [ -d ".git" ]; then
  echo "Git pull"
  git pull --rebase
else
  echo "Не git-проект — пропускаем git pull"
fi

echo "Пересобираем и запускаем контейнеры"
docker compose up -d --build

echo "Применяем миграции"
docker compose exec backend python manage.py makemigrations --noinput || echo "Нет новых миграций"
docker compose exec backend python manage.py migrate --noinput

echo "Собираем статику"
docker compose exec backend python manage.py collectstatic --noinput

echo "Деплой завершён!"
