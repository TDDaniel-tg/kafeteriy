#!/usr/bin/env bash
set -euo pipefail

# Скрипт создания резервной копии базы данных «Кафетерий льгот»
BACKUP_DIR="${BACKUP_DIR:-./backups}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/cafeteria_backup_${TIMESTAMP}.sql.gz"

mkdir -p "${BACKUP_DIR}"

echo "=== Создание резервной копии БД ==="

if [ -f "backend/db.sqlite3" ]; then
    echo "Создание копии SQLite базы данных..."
    sqlite3 backend/db.sqlite3 ".backup '${BACKUP_DIR}/cafeteria_sqlite_${TIMESTAMP}.db'"
    gzip -f "${BACKUP_DIR}/cafeteria_sqlite_${TIMESTAMP}.db"
    echo "Копия создана: ${BACKUP_DIR}/cafeteria_sqlite_${TIMESTAMP}.db.gz"
elif command -v pg_dump >/dev/null 2>&1; then
    DB_NAME="${POSTGRES_DB:-cafeteria_db}"
    DB_USER="${POSTGRES_USER:-cafeteria_user}"
    DB_HOST="${POSTGRES_HOST:-localhost}"
    DB_PORT="${POSTGRES_PORT:-5432}"

    echo "Создание дампа PostgreSQL: ${DB_NAME} на ${DB_HOST}:${DB_PORT}..."
    pg_dump -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" | gzip > "${BACKUP_FILE}"
    echo "Дамп успешно создан: ${BACKUP_FILE}"
else
    echo "Используется docker compose для создания дампа контейнера db..."
    docker compose exec -T db pg_dump -U cafeteria_user -d cafeteria_db | gzip > "${BACKUP_FILE}"
    echo "Дамп успешно создан: ${BACKUP_FILE}"
fi

echo "=== Резервное копирование завершено успешно ==="
