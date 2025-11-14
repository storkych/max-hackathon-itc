from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .... import models
from ....serializers import (
    AccessControlEventSerializer,
    MaxBotWebhookSerializer,
    PaymentProviderWebhookSerializer,
    TrackerWebhookEventSerializer,
)


class AccessControlIngestView(APIView):
    """Приём batch-событий проходов СКУД."""

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        items = request.data if isinstance(request.data, list) else [request.data]
        events = []
        for item in items:
            events.append(
                models.AccessControlEvent(
                    device_id=item.get("device_id"),
                    subject_id=item.get("subject_id"),
                    direction=item.get("direction", "in"),
                    occurred_at=item.get("ts"),
                    payload=item,
                )
            )
        models.AccessControlEvent.objects.bulk_create(events)
        return Response(status=status.HTTP_202_ACCEPTED)


class TrackerWebhookView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        event = models.TrackerWebhookEvent.objects.create(
            project=None,
            external_id=request.data.get("id"),
            event_type=request.data.get("event"),
            payload=request.data,
        )
        return Response(TrackerWebhookEventSerializer(event).data, status=status.HTTP_202_ACCEPTED)


class PaymentWebhookView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        event = models.PaymentProviderWebhook.objects.create(
            intent_id=request.data.get("intent_id"),
            event_type=request.data.get("event"),
            payload=request.data,
        )
        return Response(PaymentProviderWebhookSerializer(event).data, status=status.HTTP_202_ACCEPTED)


class MaxBotWebhookView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        event = models.MaxBotWebhook.objects.create(
            user=None,
            update_type=request.data.get("type", "event"),
            payload=request.data,
        )
        return Response(MaxBotWebhookSerializer(event).data, status=status.HTTP_202_ACCEPTED)

