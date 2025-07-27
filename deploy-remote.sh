#!/bin/bash

REMOTE_HOST=selfstorage
REMOTE_DIR=/home/ubuntu/selfstorage

echo "Копируем проект на сервер"
rsync -avz \
  --exclude 'venv/' \
  --exclude '.git/' \
  --exclude '.env' \
  ./ $REMOTE_HOST:$REMOTE_DIR

echo "Запускаем удалённый деплой"
ssh $REMOTE_HOST "cd $REMOTE_DIR && ./deploy.sh"
