#!/bin/bash

set -e

cd "$(dirname "$0")" || exit 1

echo "Обновление проекта SelfStorage"

echo "Git pull (если это репозиторий)"
if [ -d ".git" ]; then
  git pull
else
  echo "Не git-проект — пропускаем git pull"
fi

echo "Пересобираем и запускаем контейнеры"
docker compose up -d --build

echo "Применяем миграции"
docker compose exec backend python manage.py migrate

echo "Собираем статику"
docker compose exec backend python manage.py collectstatic --noinput

echo "Деплой завершён!"
