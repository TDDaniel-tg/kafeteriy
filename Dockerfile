# Unified Multi-Stage Dockerfile for «Кафетерий льгот»
# Author: TDDaniel - https://tddaniel.netlify.app

# --- Stage 1: Build React 19 Frontend ---
FROM node:22-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build

# --- Stage 2: Production Python & Django Server ---
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

WORKDIR /app/backend

RUN mkdir -p /app/backend/media /app/backend/staticfiles

EXPOSE 8000

# Run migrations, seed realistic demo data, and start gunicorn
CMD python manage.py migrate --noinput && \
    python manage.py seed_demo_data && \
    gunicorn core.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2
