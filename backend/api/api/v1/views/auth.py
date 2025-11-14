from datetime import timedelta
from secrets import token_urlsafe

from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api import models
from api.serializers import LoginRequestSerializer
from api.services import (
    UniversityAuthInvalidCredentials,
    UniversityAuthServiceUnavailable,
    authenticate_user,
)
from api.utils import parse_init_data_payload

INIT_DATA_META_KEY = "HTTP_X_MAX_INIT_DATA"


def _serialize_profile(profile: models.UserProfile) -> dict:
    return {
        "id": str(profile.id),
        "user_id": profile.user_id,
        "role": profile.role,
        "scopes": profile.scopes,
        "full_name": profile.full_name,
        "email": profile.email,
        "locale": profile.locale,
        "time_zone": profile.time_zone,
    }


class AuthMeView(APIView):
    """Возвращает профиль пользователя на основе данных X-Max-Init-Data."""

    authentication_classes: list = []
    permission_classes: list = []

    def get(self, request):
        raw_init_data = request.META.get(INIT_DATA_META_KEY)
        init_payload = parse_init_data_payload(raw_init_data)
        user_payload = init_payload.get("user") or {}

        user_id = str(user_payload.get("id") or "")
        if not user_id:
            return Response(
                {"detail": "Unable to determine user id."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        role = models.UserProfile.ROLE_APPLICANT

        scopes = []
        if isinstance(scopes, str):
            scopes = [scope.strip() for scope in scopes.split(",") if scope.strip()]
        elif not isinstance(scopes, list):
            scopes = []

        first_name = user_payload.get("first_name") or ""
        last_name = user_payload.get("last_name") or ""
        full_name = (
            user_payload.get("full_name")
            or user_payload.get("name")
            or " ".join(part for part in [first_name, last_name] if part)
        )

        defaults = {
            "role": role,
            "scopes": scopes,
            "full_name": full_name,
            "email": user_payload.get("email") or "",
            "locale": user_payload.get("language_code") or "",
            "time_zone": user_payload.get("time_zone") or "",
            "metadata": init_payload,
        }

        with transaction.atomic():
            profile, created = models.UserProfile.objects.get_or_create(
                user_id=user_id,
                defaults=defaults,
            )

            # if not created:
            #     update_fields: list[str] = []
            #     for field, value in defaults.items():
            #         if value is None:
            #             continue
            #         if getattr(profile, field) != value:
            #             setattr(profile, field, value)
            #             update_fields.append(field)

            #     if update_fields:
            #         profile.save(update_fields=update_fields)

        return Response({"user": _serialize_profile(profile)})


class LoginView(APIView):
    """Авторизация по логину и паролю через условный API университета."""

    authentication_classes: list = []
    permission_classes: list = []
    serializer_class = LoginRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        login = serializer.validated_data["login"]
        password = serializer.validated_data["password"]

        raw_init_data = request.META.get(INIT_DATA_META_KEY)
        if not raw_init_data:
            return Response(
                {"detail": "X-Max-Init-Data header is required."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        init_payload = parse_init_data_payload(raw_init_data)
        user_payload = init_payload.get("user") or {}
        user_id = str(user_payload.get("id") or "")
        if not user_id:
            return Response(
                {"detail": "Unable to determine user id from init data."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        profile = models.UserProfile.objects.filter(user_id=user_id).first()
        if profile is None:
            return Response(
                {"detail": "User profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            auth_result = authenticate_user(login, password)
        except UniversityAuthInvalidCredentials:
            return Response(
                {"detail": "Invalid login or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except UniversityAuthServiceUnavailable:
            return Response(
                {"detail": "University authentication service unavailable."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        valid_roles = {choice[0] for choice in models.UserProfile.ROLE_CHOICES}
        role = auth_result.role if auth_result.role in valid_roles else profile.role

        scopes = auth_result.scopes
        if isinstance(scopes, str):
            scopes = [scope.strip() for scope in scopes.split(",") if scope.strip()]
        elif not isinstance(scopes, list):
            scopes = profile.scopes

        metadata_payload = profile.metadata or {}
        metadata_payload.setdefault("auth", {})
        metadata_payload["auth"].update(
            {
                "source": "university_api",
                "login": login,
                "university_profile": auth_result.metadata,
                "issued_at": timezone.now().isoformat(),
            }
        )

        update_fields: list[str] = []
        if profile.role != role:
            profile.role = role
            update_fields.append("role")

        if scopes != profile.scopes:
            profile.scopes = scopes
            update_fields.append("scopes")

        if auth_result.full_name and auth_result.full_name != profile.full_name:
            profile.full_name = auth_result.full_name
            update_fields.append("full_name")

        if auth_result.email and auth_result.email != profile.email:
            profile.email = auth_result.email
            update_fields.append("email")

        locale_value = auth_result.metadata.get("locale")
        if locale_value and locale_value != profile.locale:
            profile.locale = locale_value
            update_fields.append("locale")

        timezone_value = auth_result.metadata.get("time_zone")
        if timezone_value and timezone_value != profile.time_zone:
            profile.time_zone = timezone_value
            update_fields.append("time_zone")

        profile.metadata = metadata_payload
        if "metadata" not in update_fields:
            update_fields.append("metadata")

        if update_fields:
            profile.save(update_fields=update_fields)

        response_payload = {
            "user": _serialize_profile(profile),
        }

        return Response(response_payload)


class LogoutView(APIView):
    """Сбрасывает роль пользователя до абитуриента."""

    authentication_classes: list = []
    permission_classes: list = []

    def post(self, request):
        raw_init_data = request.META.get(INIT_DATA_META_KEY)
        if not raw_init_data:
            return Response(
                {"detail": "X-Max-Init-Data header is required."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        init_payload = parse_init_data_payload(raw_init_data)
        user_payload = init_payload.get("user") or {}
        user_id = str(user_payload.get("id") or "")
        if not user_id:
            return Response(
                {"detail": "Unable to determine user id from init data."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        profile = models.UserProfile.objects.filter(user_id=user_id).first()
        if profile is None:
            return Response(
                {"detail": "User profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if profile.role != models.UserProfile.ROLE_APPLICANT:
            profile.role = models.UserProfile.ROLE_APPLICANT
            profile.save(update_fields=["role"])

        return Response({"user": _serialize_profile(profile)}, status=status.HTTP_200_OK)
