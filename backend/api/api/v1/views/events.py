from django.db.models import Q
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from .... import models
from ....serializers import (
    CampusEventSerializer,
    EventRegistrationCreateSerializer,
    EventRegistrationSerializer,
)
from ..views.careers import resolve_user_from_request


class EventsPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


class EventsListView(ListAPIView):
    serializer_class = CampusEventSerializer
    pagination_class = EventsPagination

    def get_queryset(self):
        params = self.request.query_params
        queryset = models.CampusEvent.objects.filter(status=models.EVENT_STATUS_SCHEDULED).order_by("starts_at")
        q = params.get("q")
        if q:
            queryset = queryset.filter(Q(title__icontains=q) | Q(description__icontains=q))
        category = params.get("category")
        if category:
            queryset = queryset.filter(category=category)
        return queryset


class EventDetailView(RetrieveAPIView):
    queryset = models.CampusEvent.objects.all()
    serializer_class = CampusEventSerializer
    lookup_field = "id"


class EventRegistrationCreateView(APIView):
    def post(self, request, event_id: str):
        event = models.CampusEvent.objects.filter(id=event_id).first()
        if not event:
            return Response({"detail": "event_not_found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = EventRegistrationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = resolve_user_from_request(request)
        if not user:
            return Response({"detail": "authentication_required"}, status=status.HTTP_401_UNAUTHORIZED)
        data = serializer.validated_data
        registration, created = models.EventRegistration.objects.get_or_create(
            event=event,
            user=user,
            defaults={"form_payload": data.get("form_payload", {})},
        )
        if not created:
            return Response({"detail": "already_registered"}, status=status.HTTP_409_CONFLICT)
        return Response(EventRegistrationSerializer(registration).data, status=status.HTTP_201_CREATED)


class EventRegistrationsMyView(ListAPIView):
    serializer_class = EventRegistrationSerializer
    pagination_class = EventsPagination

    def get_queryset(self):
        user = resolve_user_from_request(self.request)
        if not user:
            raise NotAuthenticated()
        return models.EventRegistration.objects.filter(user=user).select_related("event").order_by("-created_at")

