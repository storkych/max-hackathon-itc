from __future__ import annotations

from typing import Iterable, List, Sequence, Tuple

from django.contrib import admin
from django.db import models
from django.forms import Textarea

from . import models as api_models

admin.site.site_title = "MAX • Admin"
admin.site.site_header = "MAX — административная панель"
admin.site.index_title = "Управление данными платформы"

DISPLAY_PRIORITY: Tuple[str, ...] = (
    "title",
    "name",
    "full_name",
    "short_title",
    "subject",
    "code",
    "user_id",
    "email",
    "status",
)

SEARCH_PRIORITY: Tuple[str, ...] = (
    "title",
    "name",
    "full_name",
    "short_title",
    "code",
    "user_id",
    "email",
    "phone",
    "slug",
    "subject",
    "description",
    "summary",
)

DATE_PRIORITY: Tuple[str, ...] = (
    "starts_at",
    "date",
    "deadline",
    "due_at",
    "due_date",
    "ends_at",
    "published_at",
    "posted_at",
    "performed_at",
    "occurred_at",
    "received_at",
    "created_at",
    "updated_at",
)

READONLY_CANDIDATES: Tuple[str, ...] = (
    "created_at",
    "updated_at",
    "generated_at",
    "processed_at",
    "performed_at",
)

LIST_DISPLAY_TYPES = (
    models.CharField,
    models.EmailField,
    models.SlugField,
    models.URLField,
    models.UUIDField,
    models.BooleanField,
    models.IntegerField,
    models.DecimalField,
    models.DateField,
    models.DateTimeField,
)

SEARCH_FIELD_TYPES = (
    models.CharField,
    models.TextField,
    models.EmailField,
    models.SlugField,
    models.UUIDField,
)

FORMFIELD_TEXTAREA_OVERRIDES = {
    models.TextField: {"widget": Textarea(attrs={"rows": 4, "cols": 100})},
    models.JSONField: {
        "widget": Textarea(
            attrs={
                "rows": 12,
                "cols": 100,
                "style": "font-family: SFMono-Regular, Menlo, Monaco, Consolas, monospace;",
            }
        )
    },
}


def _concrete_fields(model) -> List[models.Field]:
    return [
        field
        for field in model._meta.get_fields()
        if getattr(field, "concrete", False) and not getattr(field, "many_to_many", False)
    ]


def _all_model_fields(model) -> List[models.Field]:
    fields: List[models.Field] = []
    for field in model._meta.get_fields():
        if field.auto_created and not field.concrete and not field.many_to_many:
            continue
        fields.append(field)
    return fields


def _field_by_name(fields: Iterable[models.Field], name: str) -> models.Field | None:
    for field in fields:
        if field.name == name:
            return field
    return None


def _build_list_display(model) -> Tuple[str, ...]:
    fields = _concrete_fields(model)
    pk_name = model._meta.pk.name
    chosen: List[str] = [pk_name]
    seen = {pk_name}

    for candidate in DISPLAY_PRIORITY:
        field = _field_by_name(fields, candidate)
        if field:
            chosen.append(candidate)
            seen.add(candidate)
        if len(chosen) >= 6:
            break

    if len(chosen) < 6:
        for field in fields:
            if field.name in seen:
                continue
            if isinstance(field, LIST_DISPLAY_TYPES) or isinstance(field, models.ForeignKey):
                chosen.append(field.name)
                seen.add(field.name)
            if len(chosen) >= 6:
                break

    if not chosen:
        return ("__str__",)

    return tuple(chosen)


def _build_search_fields(model) -> Tuple[str, ...]:
    fields = _all_model_fields(model)
    search: List[str] = []
    seen = set()

    for candidate in SEARCH_PRIORITY:
        field = _field_by_name(fields, candidate)
        if field and isinstance(field, SEARCH_FIELD_TYPES):
            search.append(candidate)
            seen.add(candidate)
        if len(search) >= 6:
            break

    if len(search) < 6:
        for field in fields:
            if field.name in seen:
                continue
            if isinstance(field, SEARCH_FIELD_TYPES):
                search.append(field.name)
                seen.add(field.name)
            if len(search) >= 6:
                break

    pk_name = model._meta.pk.name
    if pk_name not in seen:
        search.append(pk_name)
        seen.add(pk_name)
    if "id" not in seen:
        search.append("id")

    return tuple(search)


def _build_list_filter(model) -> Tuple[str, ...]:
    filters: List[str] = []
    for field in _all_model_fields(model):
        if len(filters) >= 8:
            break
        if field.name in filters:
            continue
        if getattr(field, "choices", None):
            filters.append(field.name)
        elif isinstance(field, models.BooleanField):
            filters.append(field.name)
        elif isinstance(field, (models.DateField, models.DateTimeField)) and field.name in READONLY_CANDIDATES:
            filters.append(field.name)
        elif isinstance(field, models.ForeignKey):
            filters.append(field.name)

    return tuple(filters)


def _build_readonly_fields(model) -> Tuple[str, ...]:
    return tuple(name for name in READONLY_CANDIDATES if _field_by_name(_all_model_fields(model), name))


def _build_select_related(model) -> Tuple[str, ...]:
    related = [
        field.name
        for field in _concrete_fields(model)
        if isinstance(field, models.ForeignKey)
    ]
    return tuple(related)


def _build_autocomplete_fields(model) -> Tuple[str, ...]:
    autocomplete = [
        field.name
        for field in _concrete_fields(model)
        if isinstance(field, models.ForeignKey)
    ]
    return tuple(autocomplete)


def _build_filter_horizontal(model) -> Tuple[str, ...]:
    return tuple(
        field.name
        for field in model._meta.local_many_to_many
        if not field.auto_created
    )


def _build_date_hierarchy(model) -> str | None:
    fields = _all_model_fields(model)
    for candidate in DATE_PRIORITY:
        field = _field_by_name(fields, candidate)
        if field and isinstance(field, (models.DateTimeField, models.DateField)):
            return candidate
    return None


def _build_ordering(model) -> Tuple[str, ...]:
    if _field_by_name(_all_model_fields(model), "created_at"):
        return ("-created_at",)
    if _field_by_name(_all_model_fields(model), "updated_at"):
        return ("-updated_at",)
    if isinstance(model._meta.pk, models.AutoField):
        return ("-id",)
    return ()


def _build_search_help_text(search_fields: Sequence[str]) -> str | None:
    if not search_fields:
        return None
    return "Поиск по полям: " + ", ".join(search_fields[:8])


def _auto_config(model) -> dict[str, object]:
    list_display = _build_list_display(model)
    search_fields = _build_search_fields(model)
    config = {
        "list_display": list_display,
        "list_display_links": tuple(list_display[:2]) if len(list_display) > 1 else list_display,
        "search_fields": search_fields,
        "search_help_text": _build_search_help_text(search_fields),
        "list_filter": _build_list_filter(model),
        "readonly_fields": _build_readonly_fields(model),
        "list_select_related": _build_select_related(model),
        "autocomplete_fields": _build_autocomplete_fields(model),
        "filter_horizontal": _build_filter_horizontal(model),
        "date_hierarchy": _build_date_hierarchy(model),
        "ordering": _build_ordering(model),
    }
    return config


class AutoConfiguredAdmin(admin.ModelAdmin):
    """Базовый класс, автоматически подбирающий конфигурацию."""

    save_on_top = True
    list_per_page = 50
    empty_value_display = "—"
    formfield_overrides = FORMFIELD_TEXTAREA_OVERRIDES

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        auto = _auto_config(model)
        cls = self.__class__

        if cls.list_display == admin.ModelAdmin.list_display:
            self.list_display = auto["list_display"]
        if cls.list_display_links == admin.ModelAdmin.list_display_links:
            self.list_display_links = auto["list_display_links"]
        if cls.search_fields == admin.ModelAdmin.search_fields:
            self.search_fields = auto["search_fields"]
            self.search_help_text = auto["search_help_text"]
        if cls.list_filter == admin.ModelAdmin.list_filter:
            self.list_filter = auto["list_filter"]
        if cls.readonly_fields == admin.ModelAdmin.readonly_fields:
            self.readonly_fields = auto["readonly_fields"]
        if cls.autocomplete_fields == admin.ModelAdmin.autocomplete_fields:
            self.autocomplete_fields = auto["autocomplete_fields"]
        if cls.filter_horizontal == admin.ModelAdmin.filter_horizontal:
            self.filter_horizontal = auto["filter_horizontal"]
        if cls.list_select_related == admin.ModelAdmin.list_select_related:
            select_related = auto["list_select_related"]
            self.list_select_related = select_related if select_related else False
        if cls.date_hierarchy == admin.ModelAdmin.date_hierarchy:
            self.date_hierarchy = auto["date_hierarchy"]
        if cls.ordering == admin.ModelAdmin.ordering:
            self.ordering = auto["ordering"]

        self._normalize_admin_configuration()

    # ------------------------------------------------------------------ utils

    def _normalize_admin_configuration(self) -> None:
        model = self.model

        # list_display_links должны ссылаться на существующие элементы list_display
        list_display: Tuple[str, ...] = tuple(self.list_display or ())
        list_display_links: Tuple[str, ...] = tuple(self.list_display_links or ())

        valid_links = tuple(name for name in list_display_links if name in list_display)
        if valid_links:
            self.list_display_links = valid_links
        elif list_display:
            self.list_display_links = (list_display[0],)
        else:
            self.list_display_links = ()

        # Список ManyToMany для filter_horizontal оставляем только локальные поля
        valid_filter_horizontal: List[str] = []
        for name in self.filter_horizontal or ():
            try:
                field = model._meta.get_field(name)
            except Exception:
                continue
            if getattr(field, "many_to_many", False) and not getattr(field, "auto_created", False):
                valid_filter_horizontal.append(name)
        self.filter_horizontal = tuple(valid_filter_horizontal)

        # Autocomplete только по существующим FK
        valid_autocomplete: List[str] = []
        for name in self.autocomplete_fields or ():
            try:
                field = model._meta.get_field(name)
            except Exception:
                continue
            if isinstance(field, models.ForeignKey):
                valid_autocomplete.append(name)
        self.autocomplete_fields = tuple(valid_autocomplete)

        # list_filter — удаляем несуществующие поля/отношения
        valid_list_filter: List[str] = []
        for item in self.list_filter or ():
            if isinstance(item, str):
                try:
                    model._meta.get_field(item)
                except Exception:
                    continue
            valid_list_filter.append(item)
        self.list_filter = tuple(valid_list_filter)


# ---------------------------------------------------------------------------
# Пользователи
# ---------------------------------------------------------------------------


@admin.register(api_models.UserProfile)
class UserProfileAdmin(AutoConfiguredAdmin):
    list_display = ("user_id", "full_name", "role", "email", "academic_group", "created_at")
    search_fields = ("user_id", "full_name", "email")
    list_filter = ("role", "locale", "time_zone")
    autocomplete_fields = ("academic_group",)


# ---------------------------------------------------------------------------
# Поступление
# ---------------------------------------------------------------------------


@admin.register(api_models.University)
class UniversityAdmin(AutoConfiguredAdmin):
    list_display = ("title", "city", "region", "language", "stats_students_total", "last_updated")
    search_fields = ("title", "short_title", "city", "region")
    list_filter = ("city", "region", "language", "feature_has_dormitory", "feature_has_military_department")


@admin.register(api_models.Faculty)
class FacultyAdmin(AutoConfiguredAdmin):
    list_display = ("title", "university", "programs_count", "short_title", "created_at")
    search_fields = ("title", "short_title", "university__title")
    autocomplete_fields = ("university",)


@admin.register(api_models.Department)
class DepartmentAdmin(AutoConfiguredAdmin):
    list_display = ("title", "university", "faculty")
    search_fields = ("title", "university__title", "faculty__title")
    autocomplete_fields = ("university", "faculty")


@admin.register(api_models.Campus)
class CampusAdmin(AutoConfiguredAdmin):
    list_display = ("title", "university", "city", "address")
    search_fields = ("title", "city", "address", "university__title")
    autocomplete_fields = ("university",)


@admin.register(api_models.Program)
class ProgramAdmin(AutoConfiguredAdmin):
    list_display = ("title", "university", "department", "level", "format", "has_budget")
    list_filter = ("level", "format", "has_budget", "language")
    search_fields = ("title", "university__title", "department__title")
    autocomplete_fields = ("university", "department")


@admin.register(api_models.ProgramExam)
class ProgramExamAdmin(AutoConfiguredAdmin):
    list_display = ("program", "subject", "exam_type", "min_score", "priority")
    search_fields = ("program__title", "subject")
    autocomplete_fields = ("program",)


@admin.register(api_models.ProgramDeadline)
class ProgramDeadlineAdmin(AutoConfiguredAdmin):
    list_display = ("program", "phase", "date", "description")
    search_fields = ("program__title", "phase", "description")
    list_filter = ("phase",)
    autocomplete_fields = ("program",)


@admin.register(api_models.ProgramScholarship)
class ProgramScholarshipAdmin(AutoConfiguredAdmin):
    list_display = ("program", "name", "amount", "currency")
    search_fields = ("program__title", "name", "description")
    autocomplete_fields = ("program",)


@admin.register(api_models.ProgramAdmissionStage)
class ProgramAdmissionStageAdmin(AutoConfiguredAdmin):
    list_display = ("program", "stage", "status", "date")
    list_filter = ("status",)
    search_fields = ("program__title", "stage")
    autocomplete_fields = ("program",)


@admin.register(api_models.ProgramFAQ)
class ProgramFAQAdmin(AutoConfiguredAdmin):
    list_display = ("program", "question")
    search_fields = ("program__title", "question", "answer")
    autocomplete_fields = ("program",)


@admin.register(api_models.ProgramCurriculum)
class ProgramCurriculumAdmin(AutoConfiguredAdmin):
    list_display = ("program", "semesters", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("program",)


@admin.register(api_models.ProgramRequirement)
class ProgramRequirementAdmin(AutoConfiguredAdmin):
    list_display = ("program", "year", "regulation_url")
    list_filter = ("year",)
    search_fields = ("program__title", "year", "regulation_url")
    autocomplete_fields = ("program",)


@admin.register(api_models.OpenDayEvent)
class OpenDayEventAdmin(AutoConfiguredAdmin):
    list_display = ("title", "university", "type", "date", "city", "registration_open")
    list_filter = ("type", "city", "registration_open")
    search_fields = ("title", "description", "university__title", "city")
    autocomplete_fields = ("university",)
    filter_horizontal = ("programs",)


@admin.register(api_models.OpenDayRegistration)
class OpenDayRegistrationAdmin(AutoConfiguredAdmin):
    list_display = ("event", "full_name", "email", "status", "created_at")
    list_filter = ("status", "event")
    search_fields = ("full_name", "email", "phone", "event__title")
    autocomplete_fields = ("event", "program", "user")


@admin.register(api_models.AdmissionsInquiry)
class AdmissionsInquiryAdmin(AutoConfiguredAdmin):
    list_display = ("full_name", "email", "topic", "status", "university", "created_at")
    list_filter = ("topic", "status", "university")
    search_fields = ("full_name", "email", "question")
    autocomplete_fields = ("user", "university", "program")


# ---------------------------------------------------------------------------
# Учебный процесс
# ---------------------------------------------------------------------------


@admin.register(api_models.AcademicGroup)
class AcademicGroupAdmin(AutoConfiguredAdmin):
    list_display = ("title", "university", "education_level", "start_year", "schedule_time_zone")
    list_filter = ("education_level", "schedule_time_zone", "university")
    search_fields = ("title", "university__title")
    autocomplete_fields = ("university", "faculty", "program")


@admin.register(api_models.Teacher)
class TeacherAdmin(AutoConfiguredAdmin):
    list_display = ("full_name", "email", "phone", "department")
    search_fields = ("full_name", "email", "phone")
    autocomplete_fields = ("department",)


@admin.register(api_models.Classroom)
class ClassroomAdmin(AutoConfiguredAdmin):
    list_display = ("name", "campus", "building", "capacity")
    list_filter = ("campus",)
    search_fields = ("name", "building", "address")
    autocomplete_fields = ("campus",)


@admin.register(api_models.AcademicCourse)
class AcademicCourseAdmin(AutoConfiguredAdmin):
    list_display = ("title", "kind", "department", "format", "term", "language")
    list_filter = ("kind", "format", "term", "language")
    search_fields = ("title", "short_title", "department__title")
    autocomplete_fields = ("department",)
    filter_horizontal = ("teachers",)


@admin.register(api_models.Lesson)
class LessonAdmin(AutoConfiguredAdmin):
    list_display = ("subject", "lesson_type", "group", "starts_at", "format", "status")
    list_filter = ("lesson_type", "format", "status")
    search_fields = ("subject", "notes", "group__title")
    autocomplete_fields = ("course", "room", "teacher", "group")


@admin.register(api_models.TeacherFeedback)
class TeacherFeedbackAdmin(AutoConfiguredAdmin):
    list_display = ("teacher", "course", "rating", "status", "anonymous", "created_at")
    list_filter = ("status", "anonymous", "rating")
    search_fields = ("teacher__full_name", "course__title", "comment")
    autocomplete_fields = ("user", "teacher", "course")


@admin.register(api_models.ElectiveEnrollment)
class ElectiveEnrollmentAdmin(AutoConfiguredAdmin):
    list_display = ("user", "course", "term", "status", "priority")
    list_filter = ("status", "term")
    search_fields = ("user__full_name", "course__title")
    autocomplete_fields = ("user", "course")


# ---------------------------------------------------------------------------
# Проектная деятельность
# ---------------------------------------------------------------------------


@admin.register(api_models.Project)
class ProjectAdmin(AutoConfiguredAdmin):
    list_display = ("title", "code", "owner_type", "status", "format", "published_at")
    list_filter = ("status", "format", "owner_type")
    search_fields = ("title", "code", "summary", "owner_user__full_name")
    autocomplete_fields = ("owner_user", "department")


@admin.register(api_models.ProjectVacancy)
class ProjectVacancyAdmin(AutoConfiguredAdmin):
    list_display = ("project", "role_code", "title", "count_open")
    list_filter = ("experience_level",)
    search_fields = ("project__title", "title", "role_code")
    autocomplete_fields = ("project",)


@admin.register(api_models.ProjectApplication)
class ProjectApplicationAdmin(AutoConfiguredAdmin):
    list_display = ("project", "user", "vacancy", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("project__title", "user__full_name", "motivation")
    autocomplete_fields = ("project", "vacancy", "user")


@admin.register(api_models.ProjectTeamMembership)
class ProjectTeamMembershipAdmin(AutoConfiguredAdmin):
    list_display = ("project", "user", "role", "role_code", "joined_at")
    list_filter = ("role",)
    search_fields = ("project__title", "user__full_name", "role_code")
    autocomplete_fields = ("project", "user")


@admin.register(api_models.ProjectTask)
class ProjectTaskAdmin(AutoConfiguredAdmin):
    list_display = ("project", "title", "status", "due_date")
    list_filter = ("status",)
    search_fields = ("project__title", "title", "description")
    autocomplete_fields = ("project",)


@admin.register(api_models.ProjectSubscription)
class ProjectSubscriptionAdmin(AutoConfiguredAdmin):
    list_display = ("project", "user")
    search_fields = ("project__title", "user__full_name")
    autocomplete_fields = ("project", "user")


# ---------------------------------------------------------------------------
# Карьера
# ---------------------------------------------------------------------------


@admin.register(api_models.CareerCompany)
class CareerCompanyAdmin(AutoConfiguredAdmin):
    list_display = ("name", "verified_partner", "site_url")
    list_filter = ("verified_partner",)
    search_fields = ("name", "description")


@admin.register(api_models.CareerVacancy)
class CareerVacancyAdmin(AutoConfiguredAdmin):
    list_display = ("title", "company", "grade", "employment", "status", "posted_at")
    list_filter = ("status", "employment", "grade")
    search_fields = ("title", "company__name", "direction")
    autocomplete_fields = ("company",)


@admin.register(api_models.CareerVacancyApplication)
class CareerVacancyApplicationAdmin(AutoConfiguredAdmin):
    list_display = ("vacancy", "user", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("vacancy__title", "user__full_name")
    autocomplete_fields = ("vacancy", "user")


@admin.register(api_models.CareerConsultation)
class CareerConsultationAdmin(AutoConfiguredAdmin):
    list_display = ("user", "topic", "preferred_channel", "status", "scheduled_at")
    list_filter = ("status", "preferred_channel")
    search_fields = ("user__full_name", "topic", "subtopic")
    autocomplete_fields = ("user", "counselor")


# ---------------------------------------------------------------------------
# Деканат и финансы
# ---------------------------------------------------------------------------


@admin.register(api_models.DeaneryCertificateRequest)
class DeaneryCertificateRequestAdmin(AutoConfiguredAdmin):
    list_display = ("user", "certificate_type", "language", "status", "created_at")
    list_filter = ("status", "certificate_type", "language")
    search_fields = ("user__full_name", "purpose")
    autocomplete_fields = ("user",)


@admin.register(api_models.TuitionInvoice)
class TuitionInvoiceAdmin(AutoConfiguredAdmin):
    list_display = ("user", "term", "amount", "currency", "status", "due_date")
    list_filter = ("status", "currency")
    search_fields = ("user__full_name", "term", "description")
    autocomplete_fields = ("user",)


@admin.register(api_models.TuitionPaymentIntent)
class TuitionPaymentIntentAdmin(AutoConfiguredAdmin):
    list_display = ("user", "amount", "currency", "status", "purpose", "created_at")
    list_filter = ("status", "purpose", "currency")
    search_fields = ("user__full_name", "invoice__id", "idempotency_key")
    autocomplete_fields = ("invoice", "user")


@admin.register(api_models.DeaneryCompensationRequest)
class DeaneryCompensationRequestAdmin(AutoConfiguredAdmin):
    list_display = ("user", "compensation_type", "amount", "status", "created_at")
    list_filter = ("status", "compensation_type", "currency")
    autocomplete_fields = ("user",)
    search_fields = ("user__full_name", "reason")


@admin.register(api_models.DeaneryTransferRequest)
class DeaneryTransferRequestAdmin(AutoConfiguredAdmin):
    list_display = ("user", "from_program", "to_program", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("user__full_name", "reason")
    autocomplete_fields = ("user", "from_program", "to_program")


@admin.register(api_models.AcademicLeaveRequest)
class AcademicLeaveRequestAdmin(AutoConfiguredAdmin):
    list_display = ("user", "leave_from", "leave_to", "status")
    list_filter = ("status",)
    search_fields = ("user__full_name", "reason")
    autocomplete_fields = ("user",)


@admin.register(api_models.DormPaymentIntent)
class DormPaymentIntentAdmin(AutoConfiguredAdmin):
    list_display = ("user", "residence", "period", "amount", "status")
    list_filter = ("status", "period")
    search_fields = ("user__full_name", "residence")
    autocomplete_fields = ("user",)


@admin.register(api_models.DormService)
class DormServiceAdmin(AutoConfiguredAdmin):
    list_display = ("title", "category", "price_amount", "price_currency")
    list_filter = ("category",)
    search_fields = ("title", "description")


@admin.register(api_models.DormServiceOrder)
class DormServiceOrderAdmin(AutoConfiguredAdmin):
    list_display = ("user", "service", "status", "scheduled_for", "completed_at")
    list_filter = ("status",)
    search_fields = ("user__full_name", "service__title")
    autocomplete_fields = ("user", "service", "payment_intent")


@admin.register(api_models.DormGuestPass)
class DormGuestPassAdmin(AutoConfiguredAdmin):
    list_display = ("user", "guest_full_name", "visit_date", "status")
    list_filter = ("status", "visit_date")
    search_fields = ("guest_full_name", "notes", "user__full_name")
    autocomplete_fields = ("user",)


@admin.register(api_models.DormSupportTicket)
class DormSupportTicketAdmin(AutoConfiguredAdmin):
    list_display = ("user", "category", "subject", "status", "created_at")
    list_filter = ("status", "category")
    search_fields = ("subject", "description", "user__full_name")
    autocomplete_fields = ("user",)


# ---------------------------------------------------------------------------
# Внеучебные события
# ---------------------------------------------------------------------------


@admin.register(api_models.CampusEvent)
class CampusEventAdmin(AutoConfiguredAdmin):
    list_display = ("title", "category", "starts_at", "ends_at", "status", "visibility")
    list_filter = ("category", "status", "visibility", "registration_required")
    search_fields = ("title", "subtitle", "description")


@admin.register(api_models.EventRegistration)
class EventRegistrationAdmin(AutoConfiguredAdmin):
    list_display = ("event", "user", "status", "created_at")
    list_filter = ("status", "event")
    search_fields = ("event__title", "user__full_name")
    autocomplete_fields = ("event", "user")


# ---------------------------------------------------------------------------
# Библиотека
# ---------------------------------------------------------------------------


@admin.register(api_models.LibraryCatalogItem)
class LibraryCatalogItemAdmin(AutoConfiguredAdmin):
    list_display = ("title", "media_type", "published_year", "language")
    list_filter = ("media_type", "language")
    search_fields = ("title", "subtitle", "authors", "isbn", "doi")


@admin.register(api_models.LibraryHold)
class LibraryHoldAdmin(AutoConfiguredAdmin):
    list_display = ("item", "user", "status", "pickup_location", "expires_at")
    list_filter = ("status", "pickup_location")
    search_fields = ("item__title", "user__full_name")
    autocomplete_fields = ("item", "user")


@admin.register(api_models.LibraryLoan)
class LibraryLoanAdmin(AutoConfiguredAdmin):
    list_display = ("item", "user", "issued_at", "due_at", "status")
    list_filter = ("status",)
    search_fields = ("item__title", "user__full_name", "barcode")
    autocomplete_fields = ("item", "user")


@admin.register(api_models.LibraryEBookAccess)
class LibraryEBookAccessAdmin(AutoConfiguredAdmin):
    list_display = ("item", "user", "status", "expires_at")
    list_filter = ("status",)
    search_fields = ("item__title", "user__full_name")
    autocomplete_fields = ("item", "user")


@admin.register(api_models.LibraryFinePaymentIntent)
class LibraryFinePaymentIntentAdmin(AutoConfiguredAdmin):
    list_display = ("user", "loan", "amount", "status")
    list_filter = ("status",)
    search_fields = ("user__full_name", "loan__item__title")
    autocomplete_fields = ("user", "loan")


# ---------------------------------------------------------------------------
# HR и сотрудники
# ---------------------------------------------------------------------------


@admin.register(api_models.HRTravelRequest)
class HRTravelRequestAdmin(AutoConfiguredAdmin):
    list_display = ("user", "title", "destination", "status", "start_date", "end_date")
    list_filter = ("status",)
    search_fields = ("user__full_name", "title", "purpose", "destination")
    autocomplete_fields = ("user",)


@admin.register(api_models.HRLeaveRequest)
class HRLeaveRequestAdmin(AutoConfiguredAdmin):
    list_display = ("user", "leave_type", "start_date", "end_date", "status")
    list_filter = ("status", "leave_type")
    search_fields = ("user__full_name", "leave_type")
    autocomplete_fields = ("user",)


@admin.register(api_models.OfficeCertificateRequest)
class OfficeCertificateRequestAdmin(AutoConfiguredAdmin):
    list_display = ("user", "certificate_type", "status", "created_at")
    list_filter = ("status", "certificate_type")
    search_fields = ("user__full_name", "purpose")
    autocomplete_fields = ("user",)


@admin.register(api_models.OfficeGuestPass)
class OfficeGuestPassAdmin(AutoConfiguredAdmin):
    list_display = ("host", "guest_full_name", "visit_date", "status")
    list_filter = ("status", "visit_date")
    search_fields = ("guest_full_name", "guest_company", "host__full_name")
    autocomplete_fields = ("host",)


# ---------------------------------------------------------------------------
# Дашборды, новости и интеграции
# ---------------------------------------------------------------------------


@admin.register(api_models.DashboardSnapshot)
class DashboardSnapshotAdmin(AutoConfiguredAdmin):
    list_display = ("slug", "date", "generated_at", "source")
    list_filter = ("slug", "date", "source")
    search_fields = ("slug", "scope", "source")


@admin.register(api_models.NewsMention)
class NewsMentionAdmin(AutoConfiguredAdmin):
    list_display = ("title", "source", "published_at", "tonality")
    list_filter = ("source", "tonality")
    search_fields = ("title", "source", "query")


@admin.register(api_models.AccessControlEvent)
class AccessControlEventAdmin(AutoConfiguredAdmin):
    list_display = ("subject_id", "device_id", "direction", "occurred_at", "processed")
    list_filter = ("processed", "direction", "user_id")
    search_fields = ("subject_id", "device_id")


@admin.register(api_models.TrackerWebhookEvent)
class TrackerWebhookEventAdmin(AutoConfiguredAdmin):
    list_display = ("event_type", "project", "status", "received_at", "processed_at")
    list_filter = ("status", "event_type")
    search_fields = ("event_type", "user_id", "project__title")
    autocomplete_fields = ("project",)


@admin.register(api_models.PaymentProviderWebhook)
class PaymentProviderWebhookAdmin(AutoConfiguredAdmin):
    list_display = ("event_type", "intent_id", "status", "received_at", "processed_at")
    list_filter = ("status", "event_type")
    search_fields = ("event_type", "intent_id")


@admin.register(api_models.MaxBotWebhook)
class MaxBotWebhookAdmin(AutoConfiguredAdmin):
    list_display = ("update_type", "user", "status", "received_at", "processed_at")
    list_filter = ("status", "update_type")
    search_fields = ("update_type", "user__full_name")
    autocomplete_fields = ("user",)


# ---------------------------------------------------------------------------
# Общие модели
# ---------------------------------------------------------------------------


@admin.register(api_models.IdempotencyKeyRecord)
class IdempotencyKeyRecordAdmin(AutoConfiguredAdmin):
    list_display = ("key", "scope", "status_code", "expires_at")
    list_filter = ("scope", "status_code", "expires_at")
    search_fields = ("key", "scope", "request_hash")


@admin.register(api_models.AuditLogEntry)
class AuditLogEntryAdmin(AutoConfiguredAdmin):
    list_display = ("action", "user", "resource", "request_id", "performed_at")
    list_filter = ("action", "performed_at")
    search_fields = ("action", "resource", "request_id", "user__full_name")
    autocomplete_fields = ("user",)

