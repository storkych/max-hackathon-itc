from __future__ import annotations

import logging

from django.http import HttpResponseForbidden

from .utils.init_data import validate_init_data, get_tg_id_from_headers

logger = logging.getLogger(__name__)

INIT_DATA_HEADER = "HTTP_X_MAX_INIT_DATA"


class InitDataValidationMiddleware:
    """
    Middleware, которая валидирует заголовок X-Max-Init-Data для запросов мини-приложения.

    Если заголовок отсутствует, запрос пропускается. Если подпись невалидна, возвращается 403.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/admin"):
            return self.get_response(request)

        init_data = request.META.get(INIT_DATA_HEADER)
        if not init_data:
            return HttpResponseForbidden("Init data is required.")
        if init_data and not validate_init_data(init_data):
            logger.warning("Запрос отклонён: подпись init_data не прошла проверку.")
            return HttpResponseForbidden("Invalid init data signature.")

        if init_data:
            tg_id = get_tg_id_from_headers({"Data-check-string": init_data})
            request.tg_id = tg_id

        return self.get_response(request)

