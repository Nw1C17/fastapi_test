#!/bin/sh
set -e

mkdir -p alembic/versions

if [ -z "$(ls -A alembic/versions 2>/dev/null)" ]; then
    echo "Миграций не найдено..."
    alembic revision --autogenerate -m "init"
fi

echo "запуск миграций..."
alembic upgrade head

echo "Starting Uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000