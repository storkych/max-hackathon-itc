# Max Campus Mini App

Платформа для мини-приложения Max Campus: backend на Django REST Framework c PostgreSQL и frontend на React/Vite. Репозиторий содержит как production-ready образы (Docker), так и dev-окружение для локальной разработки.

## Архитектура

- `backend/` — Django 5 + DRF, Postgres 16, gunicorn и nginx-прокси.
- `frontend/app/` — SPA на React 19 + Vite 7 + TypeScript.

## Структура репозитория

```
backend/
  config/…          # Django settings (split settings)
  api/api/v1/…      # DRF views + сериализаторы
  deploy/           # Dockerfile'ы для Django и nginx
  docker-compose*.yml
frontend/
  app/              # React/Vite приложение
  Dockerfile        # prod-билд c nginx
  docker-compose.yml
```

## Предварительные требования

- Python 3.12, pip, virtualenv
- Node.js 20+ и npm 10+
- Docker Engine + Docker Compose v2 (для контейнеров и локального Postgres)

## Переменные окружения для backend

Создайте файл `backend/.env.dev` (используется и при `runserver`, и docker-compose_dev). Минимальный набор:

```
SECRET_KEY=dev-secret
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8000,http://localhost:8000

POSTGRES_DB=maxcampus
POSTGRES_USER=maxcampus
POSTGRES_PASSWORD=maxcampus
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432

BOT_TOKEN=test-bot-token
```

Дополнительно можно задать `UNIVERSITY_AUTH_FIXTURES`, `UNIVERSITY_SCHEDULE_FIXTURES` (JSON) и `ALLOWED_HOSTS`/`CSRF_TRUSTED_ORIGINS` для прода. Для production-стека используйте `backend/.env.prod` с теми же ключами.

## Локальный запуск (Python + Node)

1. ### Поднять Postgres
   ```bash
   cd /backend
   docker compose -f docker-compose_dev.yml up -d
   ```

2. ### Установить зависимости backend
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. ### Применить миграции и наполнить данными
   ```bash
   python manage.py migrate
   ```

4. ### Запустить backend
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

5. ### Запустить frontend (Vite)
   ```bash
   cd ../frontend/app
   npm install
   npm run dev -- --host
   ```
   По умолчанию Vite слушает `http://localhost:5173`. Переопределите API-адрес через `frontend/app/.env.local`:
   ```
   VITE_API_BASE_URL=http://localhost:8000/api/v1
   VITE_API_ACCESS_TOKEN=local-demo-token
   ```

## Запуск в Docker

### Backend (Django + Postgres + nginx)

```bash
cd /backend
docker compose up --build
```

- `web` — образ из `deploy/django/Dockerfile` (gunicorn на 8000).
- `db` — PostgreSQL 16 (`5111` наружу по умолчанию).
- `nginx-django-api` — пробрасывает API на `http://localhost:8600/api/v1`.
- Статика монтируется в volume `max-student-mini-app-backend-static-volume`.

### Frontend (nginx + статические сборки)

```bash
cd /frontend
docker compose up --build
```

- Stage `builder` собирает Vite (`npm run build`).
- Nginx слушает `5176` и проксирует статику из `dist/`.
- Для работы с backend пропишите `VITE_API_BASE_URL=http://host.docker.internal:8600/api/v1` перед билдом (`ARG` не требуется — Vite читает `.env.production` во время `npm run build`).
