from rest_framework import status
from rest_framework.exceptions import NotAuthenticated
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from .... import models
from ....serializers import (
    AcademicLeaveCreateSerializer,
    AcademicLeaveRequestSerializer,
    DeaneryCertificateCreateSerializer,
    DeaneryCertificateRequestSerializer,
    DeaneryCompensationCreateSerializer,
    DeaneryCompensationRequestSerializer,
    DeaneryTransferCreateSerializer,
    DeaneryTransferRequestSerializer,
    TuitionInvoiceSerializer,
    TuitionPaymentIntentCreateSerializer,
    TuitionPaymentIntentSerializer,
)
from ..views.careers import resolve_user_from_request


class DeaneryPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


class DeaneryCertificateCreateView(APIView):
    def post(self, request):
        serializer = DeaneryCertificateCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = resolve_user_from_request(request)
        if not user:
            return Response({"detail": "authentication_required"}, status=status.HTTP_401_UNAUTHORIZED)
        request_obj = models.DeaneryCertificateRequest.objects.create(
            user=user,
            certificate_type=serializer.validated_data["certificate_type"],
            language=serializer.validated_data.get("language") or "",
            purpose=serializer.validated_data.get("purpose") or "",
            copies_count=serializer.validated_data.get("copies_count", 1),
            delivery_method=serializer.validated_data["delivery_method"],
            pickup_location=serializer.validated_data.get("pickup_location") or "",
            digital_copy=serializer.validated_data.get("digital_copy", False),
            attachments=serializer.validated_data.get("attachments", []),
        )
        return Response(DeaneryCertificateRequestSerializer(request_obj).data, status=status.HTTP_201_CREATED)


class DeaneryCertificateListView(ListAPIView):
    serializer_class = DeaneryCertificateRequestSerializer
    pagination_class = DeaneryPagination

    def get_queryset(self):
        user = resolve_user_from_request(self.request)
        if not user:
            raise NotAuthenticated()
        return models.DeaneryCertificateRequest.objects.filter(user=user).order_by("-created_at")


class DeaneryTuitionInvoiceCreateView(APIView):
    def post(self, request):
        serializer = TuitionInvoiceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = resolve_user_from_request(request)
        if not user:
            return Response({"detail": "authentication_required"}, status=status.HTTP_401_UNAUTHORIZED)
        invoice = models.TuitionInvoice.objects.create(
            user=user,
            term=serializer.validated_data["term"],
            amount=serializer.validated_data["amount"],
            currency=serializer.validated_data.get("currency", "RUB"),
            due_date=serializer.validated_data["due_date"],
            description=serializer.validated_data.get("description", ""),
            status=serializer.validated_data.get("status", "pending"),
            paid_at=serializer.validated_data.get("paid_at"),
            payment_method=serializer.validated_data.get("payment_method", ""),
            metadata=serializer.validated_data.get("metadata", {}),
        )
        return Response(TuitionInvoiceSerializer(invoice).data, status=status.HTTP_201_CREATED)


class TuitionInvoiceListView(ListAPIView):
    serializer_class = TuitionInvoiceSerializer
    pagination_class = DeaneryPagination

    def get_queryset(self):
        user = resolve_user_from_request(self.request)
        if not user:
            raise NotAuthenticated()
        return models.TuitionInvoice.objects.filter(user=user).order_by("due_date")


class TuitionPaymentIntentCreateView(APIView):
    def post(self, request):
        serializer = TuitionPaymentIntentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = resolve_user_from_request(request)
        if not user:
            return Response({"detail": "authentication_required"}, status=status.HTTP_401_UNAUTHORIZED)
        invoice = None
        if data.get("invoice_id"):
            invoice = models.TuitionInvoice.objects.filter(id=data["invoice_id"], user=user).first()
        intent = models.TuitionPaymentIntent.objects.create(
            invoice=invoice,
            user=user,
            amount=data["amount"],
            currency=data.get("currency", "RUB"),
            purpose=data.get("purpose") or "tuition",
            status=models.PAYMENT_INTENT_STATUS_REQUIRES_ACTION,
        )
        return Response(TuitionPaymentIntentSerializer(intent).data, status=status.HTTP_201_CREATED)


class TuitionPaymentIntentListView(ListAPIView):
    serializer_class = TuitionPaymentIntentSerializer
    pagination_class = DeaneryPagination

    def get_queryset(self):
        user = resolve_user_from_request(self.request)
        if not user:
            raise NotAuthenticated()
        return (
            models.TuitionPaymentIntent.objects.filter(user=user)
            .select_related("invoice")
            .order_by("-created_at")
        )


class DeaneryCompensationCreateView(APIView):
    def post(self, request):
        serializer = DeaneryCompensationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = resolve_user_from_request(request)
        if not user:
            return Response({"detail": "authentication_required"}, status=status.HTTP_401_UNAUTHORIZED)
        req = models.DeaneryCompensationRequest.objects.create(
            user=user,
            compensation_type=data["compensation_type"],
            amount=data["amount"],
            currency=data.get("currency", "RUB"),
            reason=data.get("reason") or "",
            bank_details=data.get("bank_details", {}),
            documents=data.get("documents", []),
        )
        return Response(DeaneryCompensationRequestSerializer(req).data, status=status.HTTP_201_CREATED)


class DeaneryCompensationListView(ListAPIView):
    serializer_class = DeaneryCompensationRequestSerializer
    pagination_class = DeaneryPagination

    def get_queryset(self):
        user = resolve_user_from_request(self.request)
        if not user:
            raise NotAuthenticated()
        return models.DeaneryCompensationRequest.objects.filter(user=user).order_by("-created_at")


class DeaneryTransferCreateView(APIView):
    def post(self, request):
        serializer = DeaneryTransferCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = resolve_user_from_request(request)
        if not user:
            return Response({"detail": "authentication_required"}, status=status.HTTP_401_UNAUTHORIZED)
        from_program = None
        to_program = None
        if data.get("from_program_id"):
            from_program = models.Program.objects.filter(id=data["from_program_id"]).first()
        if data.get("to_program_id"):
            to_program = models.Program.objects.filter(id=data["to_program_id"]).first()
        req = models.DeaneryTransferRequest.objects.create(
            user=user,
            from_program=from_program,
            to_program=to_program,
            desired_term=data.get("desired_term") or "",
            reason=data.get("reason") or "",
            documents=data.get("documents", []),
        )
        return Response(DeaneryTransferRequestSerializer(req).data, status=status.HTTP_201_CREATED)


class DeaneryTransferListView(ListAPIView):
    serializer_class = DeaneryTransferRequestSerializer
    pagination_class = DeaneryPagination

    def get_queryset(self):
        user = resolve_user_from_request(self.request)
        if not user:
            raise NotAuthenticated()
        return models.DeaneryTransferRequest.objects.filter(user=user).order_by("-created_at")


class AcademicLeaveCreateView(APIView):
    def post(self, request):
        serializer = AcademicLeaveCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = resolve_user_from_request(request)
        if not user:
            return Response({"detail": "authentication_required"}, status=status.HTTP_401_UNAUTHORIZED)
        leave = models.AcademicLeaveRequest.objects.create(
            user=user,
            reason=data["reason"],
            leave_from=data["leave_from"],
            leave_to=data["leave_to"],
            documents=data.get("documents", []),
            advisor=data.get("advisor") or "",
        )
        return Response(AcademicLeaveRequestSerializer(leave).data, status=status.HTTP_201_CREATED)


class AcademicLeaveListView(ListAPIView):
    serializer_class = AcademicLeaveRequestSerializer
    pagination_class = DeaneryPagination

    def get_queryset(self):
        user = resolve_user_from_request(self.request)
        if not user:
            raise NotAuthenticated()
        return models.AcademicLeaveRequest.objects.filter(user=user).order_by("-created_at")

