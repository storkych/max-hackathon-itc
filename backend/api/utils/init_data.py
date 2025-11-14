from __future__ import annotations

import hashlib
import hmac
import json
import logging
from typing import Any, Dict, Optional
from urllib.parse import parse_qs, parse_qsl, unquote, unquote_plus

from django.conf import settings

logger = logging.getLogger(__name__)


def validate_init_data(init_data: str) -> bool:
    """
    Валидирует init_data с использованием HMAC SHA256.
    """
    bot_token = getattr(settings, "BOT_TOKEN", "")

    if not init_data:
        logger.warning("Отсутствует заголовок Data-check-string.")
        return False

    if not bot_token:
        logger.error("Не задан BOT_TOKEN в настройках. Валидация невозможна.")
        return False

    try:
        vals = {k: unquote(v) for k, v in parse_qsl(init_data)}
    except Exception as exc:
        logger.error("Ошибка при парсинге init_data: %s", exc)
        return False

    hash_value = vals.pop("hash", None)
    if not hash_value:
        logger.warning("Отсутствует хэш в init_data.")
        return False

    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(vals.items()))
    secret_key = hmac.new(
        "WebAppData".encode(),
        bot_token.encode(),
        hashlib.sha256,
    ).digest()

    generated_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256,
    ).hexdigest()

    is_valid = hmac.compare_digest(generated_hash, hash_value)
    if not is_valid:
        logger.warning("Неверный хэш данных.")
    return is_valid


def parse_init_data_payload(init_data: str) -> Dict[str, Any]:
    """
    Разобрать init_data в словарь, декодируя JSON-поля.
    """
    parsed: Dict[str, Any] = {}
    for key, value in parse_qsl(init_data, keep_blank_values=True):
        decoded_value = unquote_plus(value)
        if key in {"user", "chat", "receiver", "payload"}:
            try:
                parsed[key] = json.loads(decoded_value)
            except json.JSONDecodeError:
                parsed[key] = decoded_value
        else:
            parsed[key] = decoded_value
    return parsed


def get_tg_id_from_headers(headers: Dict[str, Any]) -> Optional[int]:
    """
    Получить Telegram user id из заголовков мини-приложения.
    """
    raw = headers.get("Data-check-string")
    if not raw:
        return None

    query_params = parse_qs(raw)
    user_values = query_params.get("user")
    if not user_values:
        return None

    try:
        user_payload = json.loads(user_values[0])
    except json.JSONDecodeError:
        logger.warning("Не удалось распарсить user из init_data")
        return None

    user_id = user_payload.get("id")
    if isinstance(user_id, int):
        return user_id

    try:
        return int(user_id)
    except (TypeError, ValueError):
        return None

