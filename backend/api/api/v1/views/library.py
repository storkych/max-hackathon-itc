from rest_framework import status
from rest_framework.exceptions import NotAuthenticated
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from .... import models
from ....serializers import (
    LibraryCatalogItemSerializer,
    LibraryEBookAccessCreateSerializer,
    LibraryEBookAccessSerializer,
    LibraryFinePaymentIntentCreateSerializer,
    LibraryFinePaymentIntentSerializer,
    LibraryHoldCreateSerializer,
    LibraryHoldSerializer,
    LibraryLoanCreateSerializer,
    LibraryLoanSerializer,
)
from ..views.careers import resolve_user_from_request


class LibraryPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


class LibraryCatalogView(ListAPIView):
    serializer_class = LibraryCatalogItemSerializer
    pagination_class = LibraryPagination

    def get_queryset(self):
        params = self.request.query_params
        queryset = models.LibraryCatalogItem.objects.all().order_by("title")
        q = params.get("q")
        if q:
            queryset = queryset.filter(title__icontains=q)
        media_type = params.get("type")
        if media_type:
            queryset = queryset.filter(media_type=media_type)
        language = params.get("language")
        if language:
            queryset = queryset.filter(language=language)
        return queryset


class LibraryHoldCreateView(APIView):
    def post(self, request):
        serializer = LibraryHoldCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = resolve_user_from_request(request)
        if not user:
            return Response({"detail": "authentication_required"}, status=status.HTTP_401_UNAUTHORIZED)
        item = models.LibraryCatalogItem.objects.filter(id=serializer.validated_data["item_id"]).first()
        if not item:
            return Response({"detail": "item_not_found"}, status=status.HTTP_404_NOT_FOUND)
        hold = models.LibraryHold.objects.create(
            item=item,
            user=user,
            pickup_location=serializer.validated_data["pickup_location"],
        )
        return Response(LibraryHoldSerializer(hold).data, status=status.HTTP_201_CREATED)


class LibraryHoldListView(ListAPIView):
    serializer_class = LibraryHoldSerializer
    pagination_class = LibraryPagination

    def get_queryset(self):
        user = resolve_user_from_request(self.request)
        if not user:
            raise NotAuthenticated()
        return models.LibraryHold.objects.filter(user=user).select_related("item").order_by("-created_at")


class LibraryLoansListView(ListAPIView):
    serializer_class = LibraryLoanSerializer
    pagination_class = LibraryPagination

    def get_queryset(self):
        user = resolve_user_from_request(self.request)
        if not user:
            raise NotAuthenticated()
        return models.LibraryLoan.objects.filter(user=user).select_related("item").order_by("due_at")


class LibraryLoanCreateView(APIView):
    def post(self, request):
        serializer = LibraryLoanCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = resolve_user_from_request(request)
        if not user:
            return Response({"detail": "authentication_required"}, status=status.HTTP_401_UNAUTHORIZED)
        item = models.LibraryCatalogItem.objects.filter(id=serializer.validated_data["item_id"]).first()
        if item is None:
            return Response({"detail": "item_not_found"}, status=status.HTTP_404_NOT_FOUND)
        loan = models.LibraryLoan.objects.create(
            item=item,
            user=user,
            barcode=serializer.validated_data.get("barcode", ""),
            issued_at=serializer.validated_data.get("issued_at"),
            due_at=serializer.validated_data.get("due_at"),
            returned_at=serializer.validated_data.get("returned_at"),
            status=serializer.validated_data.get("status", models.LOAN_STATUS_ACTIVE),
            renewals=serializer.validated_data.get("renewals", []),
            fines=serializer.validated_data.get("fines", {}),
            metadata=serializer.validated_data.get("metadata", {}),
        )
        return Response(LibraryLoanSerializer(loan).data, status=status.HTTP_201_CREATED)


class LibraryEBookAccessListView(ListAPIView):
    serializer_class = LibraryEBookAccessSerializer
    pagination_class = LibraryPagination

    def get_queryset(self):
        user = resolve_user_from_request(self.request)
        if not user:
            raise NotAuthenticated()
        return models.LibraryEBookAccess.objects.filter(user=user).select_related("item").order_by(
            "-created_at"
        )


class LibraryEBookAccessCreateView(APIView):
    def post(self, request):
        serializer = LibraryEBookAccessCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = resolve_user_from_request(request)
        if not user:
            return Response({"detail": "authentication_required"}, status=status.HTTP_401_UNAUTHORIZED)
        item = models.LibraryCatalogItem.objects.filter(id=serializer.validated_data["item_id"]).first()
        if item is None:
            return Response({"detail": "item_not_found"}, status=status.HTTP_404_NOT_FOUND)
        access = models.LibraryEBookAccess.objects.create(
            item=item,
            user=user,
            status=serializer.validated_data.get("status", models.EBOOK_ACCESS_STATUS_PENDING),
            access_url=serializer.validated_data.get("access_url", ""),
            expires_at=serializer.validated_data.get("expires_at"),
            device_limit=serializer.validated_data.get("device_limit"),
            drm_info=serializer.validated_data.get("drm_info", {}),
            metadata=serializer.validated_data.get("metadata", {}),
            idempotency_key=serializer.validated_data.get("idempotency_key", ""),
            request_id=serializer.validated_data.get("request_id", ""),
        )
        return Response(LibraryEBookAccessSerializer(access).data, status=status.HTTP_201_CREATED)


class LibraryFinePaymentIntentCreateView(APIView):
    def post(self, request):
        serializer = LibraryFinePaymentIntentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = resolve_user_from_request(request)
        if not user:
            return Response({"detail": "authentication_required"}, status=status.HTTP_401_UNAUTHORIZED)
        loan = None
        if data.get("loan_id"):
            loan = models.LibraryLoan.objects.filter(id=data["loan_id"], user=user).first()
        intent = models.LibraryFinePaymentIntent.objects.create(
            user=user,
            loan=loan,
            amount=data["amount"],
            currency=data.get("currency", "RUB"),
        )
        return Response(LibraryFinePaymentIntentSerializer(intent).data, status=status.HTTP_201_CREATED)


class LibraryFinePaymentIntentListView(ListAPIView):
    serializer_class = LibraryFinePaymentIntentSerializer
    pagination_class = LibraryPagination

    def get_queryset(self):
        user = resolve_user_from_request(self.request)
        if not user:
            raise NotAuthenticated()
        return (
            models.LibraryFinePaymentIntent.objects.filter(user=user)
            .select_related("loan", "loan__item")
            .order_by("-created_at")
        )

 