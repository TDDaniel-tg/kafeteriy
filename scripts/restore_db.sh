#!/usr/bin/env bash
set -euo pipefail

# Скрипт восстановления базы данных «Кафетерий льгот» из резервной копии
if [ $# -lt 1 ]; then
    echo "Использование: $0 <путь_к_файлу_дампа>"
    echo "Пример: $0 backups/cafeteria_backup_20251001_120000.sql.gz"
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "${BACKUP_FILE}" ]; then
    echo "Ошибка: файл ${BACKUP_FILE} не найден!"
    exit 1
fi

echo "=== Восстановление БД из ${BACKUP_FILE} ==="

if [[ "${BACKUP_FILE}" == *"sqlite"* ]]; then
    echo "Восстановление SQLite базы..."
    gunzip -c "${BACKUP_FILE}" > backend/db.sqlite3
    echo "База успешно восстановлена в backend/db.sqlite3"
elif command -v psql >/dev/null 2>&1; then
    DB_NAME="${POSTGRES_DB:-cafeteria_db}"
    DB_USER="${POSTGRES_USER:-cafeteria_user}"
    DB_HOST="${POSTGRES_HOST:-localhost}"
    DB_PORT="${POSTGRES_PORT:-5432}"

    echo "Восстановление PostgreSQL базы ${DB_NAME}..."
    gunzip -c "${BACKUP_FILE}" | psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}"
    echo "Восстановление завершено успешно."
else
    echo "Используется docker compose для восстановления контейнера db..."
    gunzip -c "${BACKUP_FILE}" | docker compose exec -T db psql -U cafeteria_user -d cafeteria_db
    echo "Восстановление завершено успешно."
fi

echo "=== База данных восстановлена ==="
