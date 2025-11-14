from django.db.models import Q
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from .... import models
from ....serializers import (
    CareerConsultationCreateSerializer,
    CareerConsultationSerializer,
    CareerVacancyApplicationCreateSerializer,
    CareerVacancyApplicationSerializer,
    CareerVacancyDetailSerializer,
    CareerVacancySerializer,
)
from ....utils.init_data import parse_init_data_payload

class CareerVacancyPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class CareerConsultationPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


def resolve_user_from_request(request):
    if hasattr(request, "_resolved_user"):
        return request._resolved_user

    user = getattr(request, "user", None)
    if getattr(user, "is_authenticated", False):
        request._resolved_user = user
        return user

    init_data = request.META.get("HTTP_X_MAX_INIT_DATA")
    if not init_data:
        request._resolved_user = None
        return None

    payload = parse_init_data_payload(init_data)
    user_payload = payload.get("user") or {}
    user_id = str(user_payload.get("id") or "")
    if not user_id:
        request._resolved_user = None
        return None

    resolved_user = models.UserProfile.objects.filter(user_id=user_id).first()
    request._resolved_user = resolved_user
    return resolved_user


class CareerVacancyListView(ListAPIView):
    serializer_class = CareerVacancySerializer
    pagination_class = CareerVacancyPagination

    def get_queryset(self):
        params = self.request.query_params
        queryset = models.CareerVacancy.objects.filter(status=models.VACANCY_STATUS_PUBLISHED).order_by("-posted_at")
        q = params.get("q")
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) | Q(company__name__icontains=q) | Q(requirements__icontains=q)
            )
        direction = params.getlist("direction")
        if direction:
            direction_q = Q()
            for direction_value in direction:
                if direction_value:
                    direction_q |= Q(direction__contains=[direction_value])
            if direction_q:
                queryset = queryset.filter(direction_q)
        grade = params.getlist("grade")
        if grade:
            queryset = queryset.filter(grade__in=grade)
        location_type = params.getlist("location_type")
        if location_type:
            queryset = queryset.filter(location__type__in=location_type)
        country = params.get("country")
        if country:
            queryset = queryset.filter(location__country__iexact=country)
        remote_only = params.get("remote_only")
        if remote_only and remote_only.lower() == "true":
            queryset = queryset.filter(location__type="remote")
        return queryset


class CareerVacancyDetailView(RetrieveAPIView):
    queryset = models.CareerVacancy.objects.all()
    serializer_class = CareerVacancyDetailSerializer
    lookup_field = "id"


class CareerVacancyApplyView(APIView):
    def post(self, request, vacancy_id: str):
        user = resolve_user_from_request(request)
        if not user:
            return Response({"detail": "authentication_required"}, status=status.HTTP_401_UNAUTHORIZED)
        vacancy = models.CareerVacancy.objects.filter(id=vacancy_id).first()
        if not vacancy:
            return Response({"detail": "vacancy_not_found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = CareerVacancyApplicationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        application, created = models.CareerVacancyApplication.objects.get_or_create(
            vacancy=vacancy,
            user=user,
            defaults={
                "resume_url": data.get("resume_url") or "",
                "cover_letter": data.get("cover_letter") or "",
                "portfolio_links": data.get("portfolio_links", []),
                "answers": data.get("answers", {}),
                "consents": data.get("consents", {}),
            },
        )
        if not created:
            return Response({"detail": "already_applied"}, status=status.HTTP_409_CONFLICT)
        return Response(CareerVacancyApplicationSerializer(application).data, status=status.HTTP_201_CREATED)


class CareerConsultationCreateView(APIView):
    def post(self, request):
        user = resolve_user_from_request(request)
        if not user:
            return Response({"detail": "authentication_required"}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = CareerConsultationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        consultation = models.CareerConsultation.objects.create(
            user=user,
            topic=serializer.validated_data["topic"],
            subtopic=serializer.validated_data.get("subtopic", ""),
            preferred_slots=serializer.validated_data.get("preferred_slots", []),
            preferred_channel=serializer.validated_data.get("preferred_channel", ""),
            status=models.CONSULTATION_STATUS_REQUESTED,
        )
        return Response(CareerConsultationSerializer(consultation).data, status=status.HTTP_201_CREATED)


class CareerConsultationListView(ListAPIView):
    serializer_class = CareerConsultationSerializer
    pagination_class = CareerConsultationPagination

    def get_queryset(self):
        user = resolve_user_from_request(self.request)
        if not user:
            raise NotAuthenticated()
        return models.CareerConsultation.objects.filter(user=user).order_by("-created_at")

