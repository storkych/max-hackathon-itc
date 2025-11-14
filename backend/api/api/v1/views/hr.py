from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .... import models
from ....serializers import (
    HRLeaveRequestCreateSerializer,
    HRLeaveRequestSerializer,
    HRTravelRequestCreateSerializer,
    HRTravelRequestSerializer,
    OfficeCertificateCreateSerializer,
    OfficeCertificateRequestSerializer,
    OfficeGuestPassCreateSerializer,
    OfficeGuestPassSerializer,
)

from .users import _resolve_profile


class HRTravelRequestCreateView(APIView):
    def post(self, request):
        profile = _resolve_profile(request)
        serializer = HRTravelRequestCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        req = models.HRTravelRequest.objects.create(
            user=profile,
            title=serializer.validated_data["title"],
            purpose=serializer.validated_data["purpose"],
            destination=serializer.validated_data["destination"],
            start_date=serializer.validated_data["start_date"],
            end_date=serializer.validated_data["end_date"],
            transport=serializer.validated_data.get("transport", {}),
            accommodations=serializer.validated_data.get("accommodations", []),
            expenses_plan=serializer.validated_data.get("expenses_plan", []),
        )
        return Response(HRTravelRequestSerializer(req).data, status=status.HTTP_201_CREATED)


class HRTravelRequestListView(ListAPIView):
    serializer_class = HRTravelRequestSerializer

    def get_queryset(self):
        profile = _resolve_profile(self.request)
        return models.HRTravelRequest.objects.filter(user=profile).order_by("-created_at")


class HRLeaveRequestCreateView(APIView):
    def post(self, request):
        profile = _resolve_profile(request)
        serializer = HRLeaveRequestCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        req = models.HRLeaveRequest.objects.create(
            user=profile,
            leave_type=serializer.validated_data["leave_type"],
            start_date=serializer.validated_data["start_date"],
            end_date=serializer.validated_data["end_date"],
            replacement=serializer.validated_data.get("replacement", {}),
        )
        return Response(HRLeaveRequestSerializer(req).data, status=status.HTTP_201_CREATED)


class HRLeaveRequestListView(ListAPIView):
    serializer_class = HRLeaveRequestSerializer

    def get_queryset(self):
        profile = _resolve_profile(self.request)
        return models.HRLeaveRequest.objects.filter(user=profile).order_by("-created_at")


class OfficeCertificateCreateView(APIView):
    def post(self, request):
        profile = _resolve_profile(request)
        serializer = OfficeCertificateCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cert = models.OfficeCertificateRequest.objects.create(
            user=profile,
            certificate_type=serializer.validated_data["certificate_type"],
            purpose=serializer.validated_data.get("purpose") or "",
            delivery=serializer.validated_data.get("delivery", {}),
        )
        return Response(OfficeCertificateRequestSerializer(cert).data, status=status.HTTP_201_CREATED)


class OfficeGuestPassCreateView(APIView):
    def post(self, request):
        profile = _resolve_profile(request)
        serializer = OfficeGuestPassCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        guest = models.OfficeGuestPass.objects.create(
            host=profile,
            guest_full_name=serializer.validated_data["guest_full_name"],
            guest_company=serializer.validated_data.get("guest_company") or "",
            visit_date=serializer.validated_data["visit_date"],
            visit_time_from=serializer.validated_data.get("visit_time_from"),
            visit_time_to=serializer.validated_data.get("visit_time_to"),
            notes=serializer.validated_data.get("notes") or "",
        )
        return Response(OfficeGuestPassSerializer(guest).data, status=status.HTTP_201_CREATED)


class OfficeGuestPassListView(ListAPIView):
    serializer_class = OfficeGuestPassSerializer

    def get_queryset(self):
        profile = _resolve_profile(self.request)
        return models.OfficeGuestPass.objects.filter(host=profile).order_by("-visit_date")

