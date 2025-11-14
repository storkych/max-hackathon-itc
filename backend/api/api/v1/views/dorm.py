from rest_framework import status
from rest_framework.exceptions import NotAuthenticated
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from .... import models
from ....serializers import (
    DormGuestPassCreateSerializer,
    DormGuestPassSerializer,
    DormPaymentIntentCreateSerializer,
    DormPaymentIntentSerializer,
    DormServiceOrderCreateSerializer,
    DormServiceOrderSerializer,
    DormServiceSerializer,
    DormSupportTicketCreateSerializer,
    DormSupportTicketSerializer,
)
from ..views.careers import resolve_user_from_request


class DormPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


class DormPaymentIntentCreateView(APIView):
    def post(self, request):
        serializer = DormPaymentIntentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = resolve_user_from_request(request)
        if not user:
            return Response({"detail": "authentication_required"}, status=status.HTTP_401_UNAUTHORIZED)
        intent = models.DormPaymentIntent.objects.create(
            user=user,
            residence=data.get("residence") or "",
            period=data.get("period") or "",
            amount=data["amount"],
            currency=data.get("currency", "RUB"),
            purpose=data.get("purpose") or "dorm_fee",
        )
        return Response(DormPaymentIntentSerializer(intent).data, status=status.HTTP_201_CREATED)


class DormPaymentIntentListView(ListAPIView):
    serializer_class = DormPaymentIntentSerializer
    pagination_class = DormPagination

    def get_queryset(self):
        user = resolve_user_from_request(self.request)
        if not user:
            raise NotAuthenticated()
        return models.DormPaymentIntent.objects.filter(user=user).order_by("-created_at")


class DormServicesListView(ListAPIView):
    serializer_class = DormServiceSerializer
    pagination_class = DormPagination

    def get_queryset(self):
        return models.DormService.objects.all().order_by("title")


class DormServiceOrderCreateView(APIView):
    def post(self, request):
        serializer = DormServiceOrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = resolve_user_from_request(request)
        if not user:
            return Response({"detail": "authentication_required"}, status=status.HTTP_401_UNAUTHORIZED)
        service = models.DormService.objects.filter(id=data["service_id"]).first()
        if not service:
            return Response({"detail": "service_not_found"}, status=status.HTTP_404_NOT_FOUND)
        order = models.DormServiceOrder.objects.create(
            user=user,
            service=service,
            payload=data.get("payload", {}),
            scheduled_for=data.get("scheduled_for"),
        )
        return Response(DormServiceOrderSerializer(order).data, status=status.HTTP_201_CREATED)


class DormServiceOrderListView(ListAPIView):
    serializer_class = DormServiceOrderSerializer
    pagination_class = DormPagination

    def get_queryset(self):
        user = resolve_user_from_request(self.request)
        if not user:
            raise NotAuthenticated()
        return (
            models.DormServiceOrder.objects.filter(user=user)
            .select_related("service")
            .order_by("-created_at")
        )


class DormGuestPassCreateView(APIView):
    def post(self, request):
        serializer = DormGuestPassCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = resolve_user_from_request(request)
        if not user:
            return Response({"detail": "authentication_required"}, status=status.HTTP_401_UNAUTHORIZED)
        guest_pass = models.DormGuestPass.objects.create(
            user=user,
            guest_full_name=data["guest_full_name"],
            guest_document=data["guest_document"],
            visit_date=data["visit_date"],
            visit_time_from=data.get("visit_time_from"),
            visit_time_to=data.get("visit_time_to"),
            notes=data.get("notes") or "",
        )
        return Response(DormGuestPassSerializer(guest_pass).data, status=status.HTTP_201_CREATED)


class DormGuestPassListView(ListAPIView):
    serializer_class = DormGuestPassSerializer
    pagination_class = DormPagination

    def get_queryset(self):
        user = resolve_user_from_request(self.request)
        if not user:
            raise NotAuthenticated()
        return models.DormGuestPass.objects.filter(user=user).order_by("-visit_date", "-created_at")


class DormSupportTicketCreateView(APIView):
    def post(self, request):
        serializer = DormSupportTicketCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = resolve_user_from_request(request)
        if not user:
            return Response({"detail": "authentication_required"}, status=status.HTTP_401_UNAUTHORIZED)
        ticket = models.DormSupportTicket.objects.create(
            user=user,
            category=data["category"],
            subject=data["subject"],
            description=data["description"],
            attachments=data.get("attachments", []),
        )
        return Response(DormSupportTicketSerializer(ticket).data, status=status.HTTP_201_CREATED)


class DormSupportTicketListView(ListAPIView):
    serializer_class = DormSupportTicketSerializer
    pagination_class = DormPagination

    def get_queryset(self):
        user = resolve_user_from_request(self.request)
        if not user:
            raise NotAuthenticated()
        return models.DormSupportTicket.objects.filter(user=user).order_by("-created_at")

