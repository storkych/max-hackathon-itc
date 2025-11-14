import base64
import json
from datetime import timedelta

from django.db import IntegrityError, transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .... import models
from ....serializers import (
    AdmissionsInquiryCreateSerializer,
    AdmissionsInquirySerializer,
    OpenDayEventSerializer,
    OpenDayRegistrationCreateSerializer,
    OpenDayRegistrationSerializer,
    ProgramDetailSerializer,
    ProgramRequirementResponseSerializer,
    ProgramRequirementSerializer,
    ProgramSerializer,
    UniversityDetailSerializer,
    UniversitySerializer,
)
from ....utils import parse_init_data_payload, validate_init_data
from ....utils.audit import write_audit_log


def _encode_cursor(id_value: str) -> str:
    payload = json.dumps({"id": id_value}).encode("utf-8")
    return base64.urlsafe_b64encode(payload).decode("utf-8")


def _decode_cursor(cursor: str) -> str:
    try:
        decoded = base64.urlsafe_b64decode(cursor.encode("utf-8")).decode("utf-8")
        data = json.loads(decoded)
        return data.get("id")
    except (ValueError, json.JSONDecodeError, TypeError):
        return ""


class UniversityListView(generics.ListAPIView):
    serializer_class = UniversitySerializer

    def get_queryset(self):
        queryset = models.University.objects.all().order_by("id")
        city = self.request.query_params.get("city")
        if city:
            queryset = queryset.filter(city__iexact=city)
        has_dormitory = self.request.query_params.get("has_dormitory")
        if has_dormitory is not None:
            queryset = queryset.filter(feature_has_dormitory=has_dormitory.lower() == "true")
        has_open_day = self.request.query_params.get("has_open_day")
        if has_open_day is not None:
            queryset = queryset.filter(feature_has_open_day=has_open_day.lower() == "true")
        cursor = self.request.query_params.get("cursor")
        if cursor:
            last_id = _decode_cursor(cursor)
            if last_id:
                queryset = queryset.filter(id__gt=last_id)
        limit = min(int(self.request.query_params.get("limit", 20)), 100)
        return queryset[: limit + 1]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        limit = min(int(self.request.query_params.get("limit", 20)), 100)
        items = queryset[:limit]
        serializer = self.get_serializer(items, many=True)
        next_cursor = None
        if len(queryset) > limit:
            next_cursor = _encode_cursor(items[-1].id)
        return Response({"items": serializer.data, "next_cursor": next_cursor})


class UniversityDetailView(generics.RetrieveAPIView):
    queryset = models.University.objects.all()
    serializer_class = UniversityDetailSerializer
    lookup_field = "id"

    def get(self, request, *args, **kwargs):
        expand = (request.query_params.get("expand") or "").split(",")
        response = super().get(request, *args, **kwargs)
        data = response.data
        if "faculties" not in expand:
            data.pop("faculties", None)
        if "campuses" not in expand:
            data.pop("campuses", None)
        if "open_days" not in expand:
            data.pop("open_days", None)
        return Response(data)


class ProgramListView(generics.ListAPIView):
    serializer_class = ProgramSerializer

    def get_queryset(self):
        params = self.request.query_params
        queryset = models.Program.objects.select_related("department", "university").all().order_by("id")
        university_id = params.get("university_id")
        if university_id:
            queryset = queryset.filter(university_id=university_id)
        level = params.get("level")
        if level:
            queryset = queryset.filter(level=level)
        format_value = params.get("format")
        if format_value:
            queryset = queryset.filter(format=format_value)
        department = params.get("department")
        if department:
            queryset = queryset.filter(department_id=department)
        duration = params.get("duration")
        if duration:
            queryset = queryset.filter(duration_years=duration)
        has_budget = params.get("has_budget")
        if has_budget is not None:
            queryset = queryset.filter(has_budget=has_budget.lower() == "true")

        cursor = params.get("cursor")
        if cursor:
            last_id = _decode_cursor(cursor)
            if last_id:
                queryset = queryset.filter(id__gt=last_id)
        limit = min(int(params.get("limit", 20)), 100)
        return queryset[: limit + 1]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        limit = min(int(self.request.query_params.get("limit", 20)), 100)
        items = queryset[:limit]
        serializer = self.get_serializer(items, many=True)
        next_cursor = None
        if len(queryset) > limit:
            next_cursor = _encode_cursor(items[-1].id)
        filters = {
            "levels": list(models.Program.objects.values_list("level", flat=True).distinct()),
            "formats": list(models.Program.objects.values_list("format", flat=True).distinct()),
            "departments": [
                {"id": dept.id, "title": dept.title}
                for dept in models.Department.objects.all().order_by("title")
            ],
        }
        return Response({"items": serializer.data, "filters": filters, "next_cursor": next_cursor})


class ProgramDetailView(generics.RetrieveAPIView):
    queryset = models.Program.objects.select_related("department", "university")
    serializer_class = ProgramDetailSerializer
    lookup_field = "id"

    def get(self, request, *args, **kwargs):
        expand = (request.query_params.get("expand") or "").split(",")
        response = super().get(request, *args, **kwargs)
        data = response.data
        if "curriculum" not in expand:
            data.pop("curriculum", None)
        if "scholarships" not in expand:
            data.pop("scholarships", None)
        if "admission_stages" not in expand:
            data.pop("admission_stages", None)
        if "faq" not in expand:
            data.pop("faq", None)
        return Response(data)


class ProgramRequirementView(APIView):
    def get(self, request):
        program_id = request.query_params.get("program_id")
        if not program_id:
            return Response(
                {"detail": "Parameter 'program_id' is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        queryset = models.ProgramRequirement.objects.filter(program_id=program_id).order_by("-year")
        year = request.query_params.get("year")
        if year:
            queryset = queryset.filter(year=year)
        requirement = queryset.first()
        if not requirement:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = ProgramRequirementResponseSerializer(requirement)
        return Response(serializer.data)


class OpenDayListView(generics.ListAPIView):
    serializer_class = OpenDayEventSerializer

    def get_queryset(self):
        params = self.request.query_params
        university_id = params.get("university_id")
        if not university_id:
            return models.OpenDayEvent.objects.none()
        queryset = models.OpenDayEvent.objects.filter(university_id=university_id).order_by("starts_at")
        program_id = params.get("program_id")
        if program_id:
            queryset = queryset.filter(programs__id=program_id)
        type_filter = params.get("type")
        if type_filter:
            queryset = queryset.filter(type=type_filter)
        city = params.get("city")
        if city:
            queryset = queryset.filter(Q(city__iexact=city))
        date_from = params.get("date_from")
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        date_to = params.get("date_to")
        if date_to:
            queryset = queryset.filter(date__lte=date_to)

        cursor = params.get("cursor")
        if cursor:
            last_id = _decode_cursor(cursor)
            if last_id:
                queryset = queryset.filter(id__gt=last_id)
        limit = min(int(params.get("limit", 20)), 100)
        return queryset.distinct()[: limit + 1]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        limit = min(int(self.request.query_params.get("limit", 20)), 100)
        items = list(queryset[:limit])
        serializer = self.get_serializer(items, many=True)
        next_cursor = None
        if len(queryset) > limit:
            next_cursor = _encode_cursor(items[-1].id)
        filters = {
            "types": list(models.OpenDayEvent.objects.values_list("type", flat=True).distinct()),
            "cities": [
                city for city in models.OpenDayEvent.objects.exclude(city="").values_list("city", flat=True).distinct()
            ],
        }
        return Response({"items": serializer.data, "filters": filters, "next_cursor": next_cursor})


class OpenDayRegistrationView(APIView):
    def post(self, request):
        serializer = OpenDayRegistrationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        idempotency_key = request.headers.get("Idempotency-Key")
        if idempotency_key:
            existing = models.OpenDayRegistration.objects.filter(idempotency_key=idempotency_key).first()
            if existing:
                return Response(
                    OpenDayRegistrationSerializer(existing).data,
                    status=status.HTTP_200_OK,
                )

        raw_init_data = request.META.get("HTTP_X_MAX_INIT_DATA")

        init_payload = parse_init_data_payload(raw_init_data)
        user_payload = init_payload.get("user") or {}
        user_id = user_payload.get("id")
        if not user_id:
            return Response({"detail": "Init data does not contain user id."}, status=status.HTTP_400_BAD_REQUEST)

        user_profile = models.UserProfile.objects.filter(user_id=str(user_id)).first()
        if not user_profile:
            return Response({"detail": "User profile not found."}, status=status.HTTP_404_NOT_FOUND)

        event = models.OpenDayEvent.objects.filter(id=data["event_id"]).first()
        if not event:
            return Response({"detail": "event_not_found"}, status=status.HTTP_404_NOT_FOUND)
        if not event.registration_open:
            return Response({"detail": "registration_closed"}, status=status.HTTP_409_CONFLICT)
        if event.registration_deadline and event.registration_deadline < timezone.now():
            return Response({"detail": "registration_closed"}, status=status.HTTP_409_CONFLICT)

        program = None
        if data.get("program_id"):
            program = models.Program.objects.filter(id=data["program_id"]).first()
            if not program:
                return Response({"detail": "program_not_found"}, status=status.HTTP_404_NOT_FOUND)
            if event.programs.exists() and not event.programs.filter(id=program.id).exists():
                return Response({"detail": "program_not_allowed"}, status=status.HTTP_409_CONFLICT)

        try:
            with transaction.atomic():
                event = models.OpenDayEvent.objects.select_for_update().get(id=event.id)
                if event.capacity is not None:
                    remaining = event.remaining if event.remaining is not None else event.capacity
                    if remaining <= 0:
                        return Response({"detail": "capacity_exhausted"}, status=status.HTTP_409_CONFLICT)
                    event.remaining = remaining - 1
                    event.save(update_fields=["remaining", "updated_at"])

                registration = models.OpenDayRegistration.objects.create(
                    event=event,
                    program=program,
                    user=user_profile,
                    full_name=data["full_name"],
                    email=data["email"],
                    phone=data.get("phone") or "",
                    comment=data.get("comment") or "",
                    status=models.OpenDayRegistration.STATUS_REGISTERED,
                    ticket={
                        "format": "qr",
                        "code": f"{event.id}-{timezone.now().timestamp():.0f}",
                    },
                    meta={
                        "created_at": timezone.now().isoformat(),
                    },
                    idempotency_key=idempotency_key or "",
                )
        except IntegrityError:
            return Response({"detail": "already_registered"}, status=status.HTTP_409_CONFLICT)

        output = OpenDayRegistrationSerializer(registration).data
        write_audit_log(
            user=user_profile,
            action="open_day_register",
            resource=f"OpenDayEvent:{event.id}",
            request_id=request.headers.get("X-Request-Id"),
            idempotency_key=idempotency_key,
            metadata={"registration_id": str(registration.id)},
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT"),
        )
        return Response(output, status=status.HTTP_201_CREATED)


class AdmissionsInquiryView(APIView):
    def post(self, request):
        serializer = AdmissionsInquiryCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        raw_init_data = request.META.get("HTTP_X_MAX_INIT_DATA")
        init_payload = parse_init_data_payload(raw_init_data)
        user_payload = init_payload.get("user") or {}
        user_id = user_payload.get("id")
        if not user_id:
            return Response({"detail": "Init data does not contain user id."}, status=status.HTTP_400_BAD_REQUEST)

        user_profile = models.UserProfile.objects.filter(user_id=str(user_id)).first()
        if not user_profile:
            return Response({"detail": "User profile not found."}, status=status.HTTP_404_NOT_FOUND)

        university = models.University.objects.filter(id=data["university_id"]).first()
        if not university:
            return Response({"detail": "university_not_found"}, status=status.HTTP_404_NOT_FOUND)

        program = None
        if data.get("program_id"):
            program = models.Program.objects.filter(id=data["program_id"]).first()
            if not program:
                return Response({"detail": "program_not_found"}, status=status.HTTP_404_NOT_FOUND)

        idempotency_key = request.headers.get("Idempotency-Key")
        if idempotency_key:
            existing = models.AdmissionsInquiry.objects.filter(idempotency_key=idempotency_key).first()
            if existing:
                return Response(AdmissionsInquirySerializer(existing).data, status=status.HTTP_200_OK)

        inquiry = models.AdmissionsInquiry.objects.create(
            user=user_profile,
            university=university,
            program=program,
            full_name=data["full_name"],
            email=data["email"],
            phone=data.get("phone") or "",
            question=data["question"],
            topic=data.get("topic") or models.AdmissionsInquiry.TOPIC_OTHER,
            consents=data.get("consents", {}),
            attachments=data.get("attachments", []),
            meta=data.get("meta", {}),
            idempotency_key=idempotency_key or "",
            status=models.AdmissionsInquiry.STATUS_RECEIVED,
            sla={
                "target_hours": 24,
                "working_hours": "09:00-18:00",
                "time_zone": university.language or "Europe/Moscow",
            },
            channels={
                "email": data["email"],
                "chat_followup": True,
            },
            tracking={
                "crm": {"enabled": False},
            },
        )
        write_audit_log(
            user=user_profile,
            action="admissions_inquiry",
            resource=f"University:{university.id}",
            request_id=request.headers.get("X-Request-Id"),
            idempotency_key=idempotency_key,
            metadata={"inquiry_id": str(inquiry.id)},
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT"),
        )
        return Response(AdmissionsInquirySerializer(inquiry).data, status=status.HTTP_201_CREATED)

