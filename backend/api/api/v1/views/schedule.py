from copy import deepcopy
from datetime import datetime, timezone as dt_timezone
from typing import Optional

from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.exceptions import NotAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .... import models
from ....serializers import (
    AcademicCourseSerializer,
    ElectiveCourseSerializer,
    ElectiveEnrollmentCreateSerializer,
    ElectiveEnrollmentSerializer,
    LessonSerializer,
    TeacherFeedbackCreateSerializer,
    TeacherFeedbackSerializer,
)
from ....utils.audit import write_audit_log
from .careers import resolve_user_from_request


def _parse_date(value: str) -> Optional[datetime]:
    try:
        return datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=dt_timezone.utc)
    except (TypeError, ValueError):
        return None


class ScheduleMyView(APIView):
    """Персональное расписание пользователя.

    В демо-режиме данные берём из условного API университета (фикстуры).
    """

    def get(self, request):
        params = request.query_params
        date_from = _parse_date(params.get("from"))
        date_to = _parse_date(params.get("to"))
        if not date_from or not date_to:
            return Response({"detail": "from/to are required in YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)

        group_id = request.query_params.get("group_id") or request.user.academic_group_id
        if not group_id:
            return Response({"detail": "group_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        schedule = self._fetch_schedule_from_university(group_id=group_id, date_from=date_from, date_to=date_to)

        time_zone = params.get("tz")
        time_zone = time_zone or "UTC"

        return Response(
            {
                "range": {
                    "from": params.get("from"),
                    "to": params.get("to"),
                    "time_zone": time_zone,
                },
                "group": {"id": group_id},
                "items": schedule,
                "meta": {
                    "generated_at": timezone.now().isoformat(),
                    "schedule_version": "v1",
                    "source": "university_api",
                },
            }
        )

    def _fetch_schedule_from_university(self, group_id: str, date_from: datetime, date_to: datetime):
        fixtures = getattr(settings, "UNIVERSITY_SCHEDULE_FIXTURES", {})
        group_schedule = fixtures.get(group_id, [])

        items = []
        for entry in group_schedule:
            starts_at = datetime.fromisoformat(entry["starts_at"])
            if not (date_from <= starts_at < date_to):
                continue
            copied = deepcopy(entry)
            copied.setdefault("id", f"{group_id}-{starts_at.isoformat()}")
            teacher = copied.get("teacher")
            if isinstance(teacher, dict):
                full_name = teacher.get("full_name") or "Неизвестный преподаватель"
                teacher["full_name"] = full_name
                teacher_id = teacher.get("id")
                if not teacher_id:
                    slug = slugify(full_name, allow_unicode=True) or "unknown"
                    teacher_id = f"teacher-{slug}"
                    teacher["id"] = teacher_id
                self._ensure_teacher_stub(teacher_id, full_name)
            items.append(copied)

        items.sort(key=lambda item: item["starts_at"])
        return items

    def _ensure_teacher_stub(self, teacher_id: str, full_name: str) -> None:
        if not teacher_id:
            return
        models.Teacher.objects.get_or_create(
            id=teacher_id,
            defaults={
                "full_name": full_name or "Неизвестный преподаватель",
                "metadata": {"source": "schedule_fixture"},
            },
        )


class ScheduleGroupView(APIView):
    """Расписание группы."""

    def get(self, request, group_id: str):
        params = request.query_params
        date_from = _parse_date(params.get("from"))
        date_to = _parse_date(params.get("to"))
        if not date_from or not date_to:
            return Response({"detail": "from/to are required"}, status=status.HTTP_400_BAD_REQUEST)

        queryset = models.Lesson.objects.filter(
            group_id=group_id,
            starts_at__gte=date_from,
            starts_at__lt=date_to,
        ).select_related("teacher", "group", "room")

        include_canceled = params.get("include_canceled", "false").lower() == "true"
        if not include_canceled:
            queryset = queryset.exclude(status=models.LESSON_STATUS_CANCELED)

        lesson_format = params.get("format")
        if lesson_format:
            queryset = queryset.filter(format=lesson_format)

        teacher_id = params.get("teacher_id")
        if teacher_id:
            queryset = queryset.filter(teacher_id=teacher_id)

        queryset = queryset.order_by("starts_at")
        serializer = LessonSerializer(queryset, many=True)
        group = models.AcademicGroup.objects.filter(id=group_id).first()
        return Response(
            {
                "group": {"id": group_id, "title": group.title if group else group_id},
                "range": {
                    "from": params.get("from"),
                    "to": params.get("to"),
                    "time_zone": params.get("tz") or "UTC",
                },
                "items": serializer.data,
                "meta": {
                    "generated_at": timezone.now().isoformat(),
                    "schedule_version": "v1",
                    "source": "schedule_core",
                },
            }
        )


class TeacherFeedbackView(APIView):
    """Отправка обратной связи о преподавателе."""

    def post(self, request):
        serializer = TeacherFeedbackCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        teacher = models.Teacher.objects.filter(id=data["teacher_id"]).first()
        if not teacher:
            return Response({"detail": "teacher_not_found"}, status=status.HTTP_404_NOT_FOUND)
        course = models.AcademicCourse.objects.filter(id=data["course_id"]).first()
        if not course:
            return Response({"detail": "course_not_found"}, status=status.HTTP_404_NOT_FOUND)

        user = resolve_user_from_request(request)
        if not user:
            return Response({"detail": "authentication_required"}, status=status.HTTP_401_UNAUTHORIZED)

        feedback, created = models.TeacherFeedback.objects.get_or_create(
            user=user,
            teacher=teacher,
            course=course,
            period=f"{timezone.now().year}",
            defaults={
                "rating": data["rating"],
                "comment": data.get("comment") or "",
                "anonymous": data.get("anonymous", True),
                "tags": data.get("tags", []),
                "status": models.TeacherFeedback.STATUS_PENDING,
            },
        )
        if not created:
            return Response({"detail": "already_submitted"}, status=status.HTTP_409_CONFLICT)
        write_audit_log(
            user=user,
            action="teacher_feedback",
            resource=f"Teacher:{teacher.id}",
            request_id=request.headers.get("X-Request-Id"),
            metadata={"feedback_id": str(feedback.id)},
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT"),
        )
        return Response(TeacherFeedbackSerializer(feedback).data, status=status.HTTP_201_CREATED)


class ElectiveCatalogView(ListAPIView):
    serializer_class = ElectiveCourseSerializer

    def get_queryset(self):
        params = self.request.query_params
        queryset = models.AcademicCourse.objects.filter(kind=models.COURSE_KIND_ELECTIVE).order_by("title")
        term = params.get("term")
        if term:
            queryset = queryset.filter(term=term)
        department = params.get("department")
        if department:
            queryset = queryset.filter(department_id=department)
        digital_faculty = params.get("digital_faculty")
        if digital_faculty is not None:
            queryset = queryset.filter(digital_faculty=digital_faculty.lower() == "true")
        lesson_format = params.get("lesson_format")
        if lesson_format:
            queryset = queryset.filter(format__icontains=lesson_format)
        language = params.get("language")
        if language:
            queryset = queryset.filter(language=language)
        return queryset

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data = {
            "term": request.query_params.get("term"),
            "items": response.data,
        }
        return response


class ElectiveEnrollmentCreateView(APIView):
    """Создание записи на электив."""

    def post(self, request):
        user = resolve_user_from_request(request)
        if not user:
            return Response({"detail": "authentication_required"}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = ElectiveEnrollmentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        course = models.AcademicCourse.objects.filter(id=data["course_id"]).first()
        if not course:
            return Response({"detail": "course_not_found"}, status=status.HTTP_404_NOT_FOUND)

        idempotency_key = request.headers.get("Idempotency-Key")
        if idempotency_key:
            existing = models.ElectiveEnrollment.objects.filter(
                user=user,
                course=course,
                idempotency_key=idempotency_key,
            ).first()
            if existing:
                return Response(ElectiveEnrollmentSerializer(existing).data, status=status.HTTP_200_OK)

        enrollment, created = models.ElectiveEnrollment.objects.get_or_create(
            user=user,
            course=course,
            term=data["term"],
            defaults={
                "priority": data.get("priority"),
                "comment": data.get("comment") or "",
                "consents": data.get("consents", {}),
                "status": models.ENROLLMENT_STATUS_PENDING,
                "idempotency_key": idempotency_key or "",
                "timestamps": {
                    "created_at": timezone.now().isoformat(),
                },
            },
        )
        if not created:
            return Response({"detail": "already_enrolled"}, status=status.HTTP_409_CONFLICT)
        write_audit_log(
            user=user,
            action="elective_enroll",
            resource=f"Course:{course.id}",
            request_id=request.headers.get("X-Request-Id"),
            idempotency_key=request.headers.get("Idempotency-Key"),
            metadata={"enrollment_id": str(enrollment.id)},
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT"),
        )
        return Response(ElectiveEnrollmentSerializer(enrollment).data, status=status.HTTP_201_CREATED)


class ElectiveEnrollmentListView(ListAPIView):
    serializer_class = ElectiveEnrollmentSerializer

    def get_queryset(self):
        user = resolve_user_from_request(self.request)
        if not user:
            raise NotAuthenticated()
        term = self.request.query_params.get("term")
        queryset = models.ElectiveEnrollment.objects.filter(user=user).select_related("course")
        if term:
            queryset = queryset.filter(term=term)
        status_filter = self.request.query_params.get("status")
        if status_filter:
            statuses = [s.strip() for s in status_filter.split(",")]
            queryset = queryset.filter(status__in=statuses)
        return queryset.order_by("-created_at")

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data = {
            "term": request.query_params.get("term"),
            "items": response.data,
        }
        return response

