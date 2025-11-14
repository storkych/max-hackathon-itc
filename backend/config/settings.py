import json
import os
from pathlib import Path

from dotenv import load_dotenv
from split_settings.tools import include

dotenv_path = os.path.join(os.path.dirname(__file__), '../.env.dev')
if os.path.isfile(dotenv_path) and os.access(dotenv_path, os.R_OK):
    load_dotenv(dotenv_path)

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY')

DEBUG = os.environ.get('DEBUG', False) == 'True'

ALLOWED_HOSTS = [host for host in (os.environ.get('ALLOWED_HOSTS') or '').split(',') if host]

CSRF_TRUSTED_ORIGINS = [origin for origin in (os.environ.get('CSRF_TRUSTED_ORIGINS') or '').split(',') if origin]

# Загружаем настройки из модулей
include(
    'components/application.py',
    'components/middleware.py',
    'components/templates.py',
    'components/database.py',
    'components/auth.py',
    'components/static.py',
    'components/drf.py',
)

CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOW_HEADERS = [
'Authorization',
'Content-Type',
'X-Max-Init-Data',
'Accept',
'Idempotency-Key',
]

ROOT_URLCONF = 'config.urls'

WSGI_APPLICATION = 'config.wsgi.application'

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

BOT_TOKEN = os.environ.get('BOT_TOKEN', '123')


def _load_university_auth_fixtures():
    raw = os.environ.get('UNIVERSITY_AUTH_FIXTURES')
    if raw:
        try:
            fixtures = json.loads(raw)
            if isinstance(fixtures, dict):
                return fixtures
        except json.JSONDecodeError:
            pass

    return {
        "student@example.com": {
            "password": "student123",
            "user_id": "student-001",
            "role": "student",
            "full_name": "Максим ",
            "email": "student@example.com",
            "scopes": ["schedule:read", "grades:read"],
        },
        "staff@example.com": {
            "password": "staff123",
            "user_id": "staff-001",
            "role": "staff",
            "full_name": "Максим",
            "email": "staff@example.com",
            "scopes": ["schedule:read", "students:manage"],
        },
        "supervisor@example.com": {
            "password": "supervisor123",
            "user_id": "supervisor-001",
            "role": "supervisor",
            "full_name": "Андрей Руководитель",
            "email": "supervisor@example.com",
            "scopes": ["schedule:read", "reports:read", "students:manage"],
        },
    }


UNIVERSITY_AUTH_FIXTURES = _load_university_auth_fixtures()


def _load_university_schedule_fixtures():
    raw = os.environ.get('UNIVERSITY_SCHEDULE_FIXTURES')
    if raw:
        try:
            fixtures = json.loads(raw)
            if isinstance(fixtures, dict):
                return fixtures
        except json.JSONDecodeError:
            pass

    return {
        "group-itmo-2024": [
            {
                "subject": "Математический анализ",
                "lesson_type": "lecture",
                "starts_at": "2024-04-01T08:30:00+03:00",
                "ends_at": "2024-04-01T10:00:00+03:00",
                "format": "offline",
                "room": {"name": "Аудитория 101", "campus": "Главный корпус"},
                "teacher": {"full_name": "Иванова А.А."},
            },
            {
                "subject": "Алгоритмы и структуры данных",
                "lesson_type": "lab",
                "starts_at": "2024-04-01T10:10:00+03:00",
                "ends_at": "2024-04-01T11:40:00+03:00",
                "format": "offline",
                "room": {"name": "Лаборатория 204", "campus": "Главный корпус"},
                "teacher": {"full_name": "Петров Б.Б."},
            },
            {
                "subject": "Математический анализ",
                "lesson_type": "seminar",
                "starts_at": "2024-04-02T12:00:00+03:00",
                "ends_at": "2024-04-02T13:30:00+03:00",
                "format": "offline",
                "room": {"name": "Аудитория 102", "campus": "Главный корпус"},
                "teacher": {"full_name": "Иванова А.А."},
            },
        ],
        "group-mipt-301": [
            {
                "subject": "Физика твердого тела",
                "lesson_type": "lecture",
                "starts_at": "2024-04-01T09:00:00+03:00",
                "ends_at": "2024-04-01T10:30:00+03:00",
                "format": "offline",
                "room": {"name": "Лекторий «Физтех Арена»", "campus": "Главный корпус"},
                "teacher": {"full_name": "Сидоров В.В."},
            },
            {
                "subject": "Машинное обучение",
                "lesson_type": "lecture",
                "starts_at": "2024-04-01T11:00:00+03:00",
                "ends_at": "2024-04-01T12:30:00+03:00",
                "format": "online",
                "room": {"name": "Zoom #123-456-789"},
                "teacher": {"full_name": "Кузнецов Г.Г."},
            },
            {
                "subject": "Физика твердого тела",
                "lesson_type": "seminar",
                "starts_at": "2024-04-02T09:00:00+03:00",
                "ends_at": "2024-04-02T10:30:00+03:00",
                "format": "offline",
                "room": {"name": "Аудитория 312", "campus": "Главный корпус"},
                "teacher": {"full_name": "Сидоров В.В."},
            },
        ],
        "group-msu-phys-101": [
            {
                "subject": "Квантовая механика",
                "lesson_type": "lecture",
                "starts_at": "2024-04-01T08:00:00+03:00",
                "ends_at": "2024-04-01T09:30:00+03:00",
                "format": "offline",
                "room": {"name": "Аудитория ФФ-201", "campus": "Главное здание"},
                "teacher": {"full_name": "Александров Д.Д."},
            },
            {
                "subject": "Дифференциальные уравнения",
                "lesson_type": "lecture",
                "starts_at": "2024-04-01T10:00:00+03:00",
                "ends_at": "2024-04-01T11:30:00+03:00",
                "format": "offline",
                "room": {"name": "Аудитория МехМата-401", "campус": "Главное здание"},
                "teacher": {"full_name": "Егорова Е.Е."},
            },
            {
                "subject": "Физический практикум",
                "lesson_type": "lab",
                "starts_at": "2024-04-02T13:00:00+03:00",
                "ends_at": "2024-04-02T16:00:00+03:00",
                "format": "offline",
                "room": {"name": "Лаборатория 2", "campус": "Физический факультет"},
                "teacher": {"full_name": "Александров Д.Д."},
            },
        ],
    }


UNIVERSITY_SCHEDULE_FIXTURES = _load_university_schedule_fixtures()

