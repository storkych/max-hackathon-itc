from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from api import models
from api.serializers import UserSettingsSerializer
from api.utils import parse_init_data_payload

from .auth import INIT_DATA_META_KEY


def _resolve_profile(request) -> models.UserProfile:
    raw_init_data = request.META.get(INIT_DATA_META_KEY)

    init_payload = parse_init_data_payload(raw_init_data)
    user_payload = init_payload.get("user") or {}

    user_id = str(user_payload.get("id") or "")
    if not user_id:
        raise exceptions.ValidationError(detail="Unable to determine user id from init data.")

    profile = models.UserProfile.objects.filter(user_id=user_id).first()
    if profile is None:
        raise exceptions.NotFound(detail="User profile not found.")

    return profile


class UserSettingsView(APIView):
    serializer_class = UserSettingsSerializer

    def get(self, request):
        profile = _resolve_profile(request)
        serializer = self.serializer_class({"settings": profile.settings or {}}, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        profile = _resolve_profile(request)
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        settings_payload = serializer.validated_data.get("settings") or {}
        profile.settings = settings_payload
        profile.save(update_fields=["settings", "updated_at"])

        return Response({"settings": settings_payload}, status=status.HTTP_200_OK)

