from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, List

from django.conf import settings

logger = logging.getLogger(__name__)


class UniversityAuthError(Exception):
    """Базовое исключение для ошибок авторизации в университете."""


class UniversityAuthInvalidCredentials(UniversityAuthError):
    """Ошибка неверного логина или пароля."""


class UniversityAuthServiceUnavailable(UniversityAuthError):
    """Ошибка недоступности сервиса авторизации университета."""


@dataclass
class UniversityAuthResult:
    user_id: str
    role: str
    scopes: List[str]
    full_name: str
    email: str
    metadata: Dict[str, Any]


def authenticate_user(login: str, password: str) -> UniversityAuthResult:
    """
    Провалидировать пользователя через условный API университета.

    Использует фикстуры из настроек, но интерфейс позволяет заменить реализацию
    на реальный HTTP-запрос.
    """

    fixtures: Dict[str, Dict[str, Any]] = getattr(settings, "UNIVERSITY_AUTH_FIXTURES", {})
    if not fixtures:
        logger.error("UNIVERSITY_AUTH_FIXTURES is empty. Authentication service unavailable.")
        raise UniversityAuthServiceUnavailable("University authentication service unavailable.")

    record = fixtures.get(login)
    if not record:
        logger.info("University auth failed: login '%s' not found.", login)
        raise UniversityAuthInvalidCredentials("Invalid login or password.")

    stored_password = str(record.get("password", ""))
    if stored_password != password:
        logger.info("University auth failed: invalid password for login '%s'.", login)
        raise UniversityAuthInvalidCredentials("Invalid login or password.")

    user_id = str(record.get("user_id") or login)
    role = str(record.get("role") or "")
    scopes = record.get("scopes") or []
    if isinstance(scopes, str):
        scopes = [scope.strip() for scope in scopes.split(",") if scope.strip()]
    elif not isinstance(scopes, list):
        scopes = []

    metadata = {key: value for key, value in record.items() if key != "password"}

    return UniversityAuthResult(
        user_id=user_id,
        role=role,
        scopes=scopes,
        full_name=record.get("full_name") or login,
        email=record.get("email") or "",
        metadata=metadata,
    )

