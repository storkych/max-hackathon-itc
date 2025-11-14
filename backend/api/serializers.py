from rest_framework import serializers

from . import models


# ---------------------------------------------------------------------------
# Аутентификация и авторизация
# ---------------------------------------------------------------------------


class LoginRequestSerializer(serializers.Serializer):
    login = serializers.CharField(max_length=128)
    password = serializers.CharField(max_length=128, trim_whitespace=False)


class UserSettingsSerializer(serializers.Serializer):
    settings = serializers.JSONField(default=dict)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["settings"] = data.get("settings") or {}
        return data


# ---------------------------------------------------------------------------
# Вспомогательные сериализаторы и функции
# ---------------------------------------------------------------------------


class ContactSerializer(serializers.Serializer):
    phone = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    site = serializers.URLField(required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)


class MediaSerializer(serializers.Serializer):
    logo_url = serializers.URLField(required=False, allow_blank=True)
    image_url = serializers.URLField(required=False, allow_blank=True)


class UniversityStatsSerializer(serializers.Serializer):
    students_total = serializers.IntegerField(required=False)
    programs_count = serializers.IntegerField(required=False)
    budget_quota = serializers.IntegerField(required=False)
    employment_rate = serializers.DecimalField(
        required=False,
        max_digits=5,
        decimal_places=2,
    )


class UniversityFeaturesSerializer(serializers.Serializer):
    has_dormitory = serializers.BooleanField(required=False)
    has_military_department = serializers.BooleanField(required=False)
    has_open_day = serializers.BooleanField(required=False)
    has_preparatory_courses = serializers.BooleanField(required=False)
    has_distance_programs = serializers.BooleanField(required=False)


class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Faculty
        fields = (
            "id",
            "title",
            "short_title",
            "description",
            "programs_count",
        )


class CampusSerializer(serializers.ModelSerializer):
    geo = serializers.SerializerMethodField()

    class Meta:
        model = models.Campus
        fields = (
            "id",
            "title",
            "address",
            "city",
            "geo",
        )

    def get_geo(self, obj):
        if obj.geo_lat is None or obj.geo_lon is None:
            return None
        return {"lat": float(obj.geo_lat), "lon": float(obj.geo_lon)}


class ProgramDepartmentSerializer(serializers.Serializer):
    id = serializers.CharField()
    title = serializers.CharField()


class ProgramUniversitySerializer(serializers.Serializer):
    id = serializers.CharField()
    title = serializers.CharField()


class ProgramExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProgramExam
        fields = ("exam_type", "subject", "min_score", "weight", "priority")
        extra_kwargs = {
            "weight": {"required": False, "allow_null": True},
            "priority": {"required": False, "allow_null": True},
        }


class ProgramDeadlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProgramDeadline
        fields = ("phase", "date", "description")


class ProgramScholarshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProgramScholarship
        fields = ("name", "amount", "currency", "description")


class ProgramAdmissionStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProgramAdmissionStage
        fields = ("stage", "status", "date", "metadata")


class ProgramFAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProgramFAQ
        fields = ("question", "answer")


class ProgramCurriculumSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProgramCurriculum
        fields = ("semesters", "core_modules", "practice", "electives", "metadata")


class ProgramRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProgramRequirement
        fields = (
            "year",
            "regulation_url",
            "exams",
            "additional_tests",
            "thresholds",
            "tuition",
            "deadlines",
            "benefits",
            "documents",
            "language_requirements",
            "international",
            "application",
            "metadata",
        )


class UniversitySerializer(serializers.ModelSerializer):
    contacts = serializers.SerializerMethodField()
    media = serializers.SerializerMethodField()
    stats = serializers.SerializerMethodField()
    features = serializers.SerializerMethodField()

    class Meta:
        model = models.University
        fields = (
            "id",
            "title",
            "short_title",
            "city",
            "region",
            "description",
            "contacts",
            "media",
            "stats",
            "features",
            "last_updated",
        )

    def get_contacts(self, obj):
        return {
            key: value
            for key, value in {
                "phone": obj.contact_phone,
                "email": obj.contact_email,
                "site": obj.contact_site,
                "address": obj.contact_address,
            }.items()
            if value
        }

    def get_media(self, obj):
        media = {
            "logo_url": obj.media_logo_url,
            "image_url": obj.media_image_url,
        }
        return {k: v for k, v in media.items() if v}

    def get_stats(self, obj):
        return {
            key: value
            for key, value in {
                "students_total": obj.stats_students_total,
                "programs_count": obj.stats_programs_count,
                "budget_quota": obj.stats_budget_quota,
                "employment_rate": obj.stats_employment_rate,
            }.items()
            if value not in (None, "")
        }

    def get_features(self, obj):
        return {
            "has_dormitory": obj.feature_has_dormitory,
            "has_military_department": obj.feature_has_military_department,
            "has_open_day": obj.feature_has_open_day,
            "has_preparatory_courses": obj.feature_has_preparatory_courses,
            "has_distance_programs": obj.feature_has_distance_programs,
        }


class UniversityDetailSerializer(UniversitySerializer):
    faculties = FacultySerializer(many=True, read_only=True)
    campuses = CampusSerializer(many=True, read_only=True)
    open_days = serializers.SerializerMethodField()
    stats = serializers.SerializerMethodField()
    features = serializers.SerializerMethodField()
    meta = serializers.SerializerMethodField()

    class Meta(UniversitySerializer.Meta):
        fields = UniversitySerializer.Meta.fields + (
            "about",
            "founded_year",
            "faculties",
            "campuses",
            "open_days",
            "stats",
            "meta",
        )

    about = serializers.CharField(source="description", required=False, allow_blank=True)
    founded_year = serializers.IntegerField(required=False, source="extra.founded_year")

    def get_open_days(self, obj):
        events = obj.open_day_events.all()
        return OpenDayEventSerializer(events, many=True).data

    def get_stats(self, obj):
        base = super().get_stats(obj)
        extra_stats = obj.extra.get("stats", {}) if isinstance(obj.extra, dict) else {}
        merged = {**extra_stats, **base}
        return merged

    def get_meta(self, obj):
        return {
            "last_updated": obj.last_updated,
            "data_source": obj.data_source,
            "lang": obj.language,
        }


class ProgramSerializer(serializers.ModelSerializer):
    department = serializers.SerializerMethodField()
    duration_years = serializers.IntegerField()
    tuition_per_year = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        allow_null=True,
    )
    exams = ProgramExamSerializer(many=True, read_only=True)

    class Meta:
        model = models.Program
        fields = (
            "id",
            "title",
            "level",
            "format",
            "department",
            "duration_years",
            "language",
            "tuition_per_year",
            "has_budget",
            "budget_places",
            "paid_places",
            "targeted_places",
            "passing_score_last_year",
            "description",
            "career_paths",
            "links",
            "media",
            "exams",
            "admission_deadline",
        )

    def get_department(self, obj):
        if not obj.department:
            return None
        return {"id": obj.department_id, "title": obj.department.title}


class ProgramDetailSerializer(ProgramSerializer):
    university = serializers.SerializerMethodField()
    quotas = serializers.SerializerMethodField()
    tuition = serializers.SerializerMethodField()
    passing_score = serializers.SerializerMethodField()
    deadlines = ProgramDeadlineSerializer(many=True, read_only=True)
    outcomes = serializers.ListField(child=serializers.CharField(), required=False)
    scholarships = ProgramScholarshipSerializer(many=True, read_only=True)
    admission_stages = ProgramAdmissionStageSerializer(many=True, read_only=True)
    faq = ProgramFAQSerializer(many=True, read_only=True)
    curriculum = ProgramCurriculumSerializer(read_only=True)

    class Meta(ProgramSerializer.Meta):
        fields = ProgramSerializer.Meta.fields + (
            "university",
            "quotas",
            "tuition",
            "passing_score",
            "deadlines",
            "outcomes",
            "scholarships",
            "admission_stages",
            "faq",
            "curriculum",
            "meta",
        )

    def get_university(self, obj):
        return {"id": obj.university_id, "title": obj.university.title}

    def get_quotas(self, obj):
        return {
            "budget_places": obj.budget_places,
            "paid_places": obj.paid_places,
            "targeted_places": obj.targeted_places,
        }

    def get_tuition(self, obj):
        if obj.tuition_per_year is None:
            return None
        return {
            "per_year": obj.tuition_per_year,
            "currency": obj.tuition_currency,
            "note": obj.tuition_note,
        }

    def get_passing_score(self, obj):
        if obj.passing_score_last_year is None:
            return None
        return {
            "last_year": obj.passing_score_last_year,
            "median": obj.passing_score_median,
            "year": obj.passing_score_year,
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["meta"] = instance.meta or {}
        return data


class ProgramRequirementResponseSerializer(serializers.Serializer):
    program = serializers.SerializerMethodField()
    campaign = serializers.SerializerMethodField()
    exams = serializers.ListField(child=serializers.DictField())
    additional_tests = serializers.ListField(child=serializers.DictField(), required=False)
    thresholds = serializers.DictField(required=False)
    tuition = serializers.DictField(required=False)
    deadlines = serializers.DictField(required=False)
    benefits = serializers.DictField(required=False)
    documents = serializers.ListField(child=serializers.DictField(), required=False)
    language_requirements = serializers.ListField(child=serializers.DictField(), required=False)
    international = serializers.DictField(required=False)
    application = serializers.DictField(required=False)
    meta = serializers.DictField(required=False)

    def get_program(self, obj: models.ProgramRequirement):
        program = obj.program
        return {
            "id": program.id,
            "title": program.title,
            "university": {"id": program.university_id, "title": program.university.title},
            "level": program.level,
            "format": program.format,
        }

    def get_campaign(self, obj: models.ProgramRequirement):
        return {
            "year": obj.year,
            "regulation_url": obj.regulation_url,
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["meta"] = instance.metadata or {}
        return data


class OpenDayEventSerializer(serializers.ModelSerializer):
    programs = serializers.SerializerMethodField()

    class Meta:
        model = models.OpenDayEvent
        fields = (
            "id",
            "type",
            "title",
            "description",
            "date",
            "starts_at",
            "ends_at",
            "location",
            "city",
            "capacity",
            "remaining",
            "registration_open",
            "registration_deadline",
            "programs",
            "media",
            "contacts",
            "links",
        )

    def get_programs(self, obj):
        programs = obj.programs.all()
        return [{"id": p.id, "title": p.title} for p in programs]


class OpenDayRegistrationSerializer(serializers.ModelSerializer):
    event = OpenDayEventSerializer(read_only=True)
    program = ProgramSerializer(read_only=True)

    class Meta:
        model = models.OpenDayRegistration
        fields = (
            "id",
            "event",
            "program",
            "status",
            "full_name",
            "email",
            "phone",
            "comment",
            "ticket",
            "notifications",
            "meta",
            "created_at",
        )
        read_only_fields = fields


class OpenDayRegistrationCreateSerializer(serializers.Serializer):
    program_id = serializers.CharField(required=True)
    event_id = serializers.CharField(required=True)
    full_name = serializers.CharField(max_length=120)
    email = serializers.EmailField()
    phone = serializers.CharField(required=False, allow_blank=True, max_length=32)
    comment = serializers.CharField(required=False, allow_blank=True, max_length=500)


class AdmissionsInquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AdmissionsInquiry
        fields = (
            "id",
            "full_name",
            "email",
            "phone",
            "question",
            "topic",
            "consents",
            "attachments",
            "meta",
            "status",
            "sla",
            "channels",
            "tracking",
            "created_at",
        )
        read_only_fields = (
            "status",
            "sla",
            "channels",
            "tracking",
            "created_at",
        )


class AdmissionsInquiryCreateSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=120)
    email = serializers.EmailField()
    phone = serializers.CharField(required=False, allow_blank=True, max_length=32)
    question = serializers.CharField(min_length=5, max_length=2000)
    university_id = serializers.CharField()
    program_id = serializers.CharField(required=False, allow_blank=True)
    topic = serializers.ChoiceField(
        choices=[choice[0] for choice in models.AdmissionsInquiry.TOPIC_CHOICES],
        required=False,
    )
    consents = serializers.DictField(child=serializers.BooleanField(), required=True)
    attachments = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        allow_empty=True,
    )
    meta = serializers.DictField(required=False)


# ---------------------------------------------------------------------------
# Сериализаторы: учебный процесс и расписание
# ---------------------------------------------------------------------------


class AcademicGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AcademicGroup
        fields = (
            "id",
            "title",
            "education_level",
            "start_year",
            "schedule_time_zone",
            "metadata",
        )


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Teacher
        fields = (
            "id",
            "full_name",
            "email",
            "phone",
            "position",
            "contacts",
            "metadata",
        )


class ClassroomSerializer(serializers.ModelSerializer):
    geo = serializers.SerializerMethodField()

    class Meta:
        model = models.Classroom
        fields = (
            "id",
            "name",
            "building",
            "address",
            "capacity",
            "equipment",
            "geo",
        )

    def get_geo(self, obj):
        campus = obj.campus
        if not campus:
            return None
        return {
            "campus_id": campus.id,
            "campus_title": campus.title,
            "geo": {
                "lat": float(campus.geo_lat) if campus.geo_lat is not None else None,
                "lon": float(campus.geo_lon) if campus.geo_lon is not None else None,
            },
        }


class LessonSerializer(serializers.ModelSerializer):
    room = serializers.SerializerMethodField()
    teacher = TeacherSerializer(read_only=True)
    group = AcademicGroupSerializer(read_only=True)

    class Meta:
        model = models.Lesson
        fields = (
            "id",
            "subject",
            "lesson_type",
            "starts_at",
            "ends_at",
            "format",
            "room",
            "teacher",
            "group",
            "subgroup",
            "links",
            "notes",
            "status",
            "series",
            "replaces",
            "cancel_info",
            "updated_remote_at",
        )

    def get_room(self, obj):
        if obj.room:
            return {
                "name": obj.room.name,
                "building": obj.room.building,
                "campus": obj.room_snapshot.get("campus") if obj.room_snapshot else None,
            }
        if obj.room_snapshot:
            return obj.room_snapshot
        return None


class AcademicCourseSerializer(serializers.ModelSerializer):
    teachers = TeacherSerializer(many=True, read_only=True)

    class Meta:
        model = models.AcademicCourse
        fields = (
            "id",
            "kind",
            "title",
            "short_title",
            "term",
            "format",
            "language",
            "ects",
            "workload_hours",
            "digital_faculty",
            "description",
            "schedule_preview",
            "quota",
            "enroll_window",
            "prerequisites",
            "anti_conflicts",
            "rating",
            "links",
            "metadata",
            "teachers",
        )


class TeacherFeedbackSerializer(serializers.ModelSerializer):
    teacher = TeacherSerializer(read_only=True)
    course = AcademicCourseSerializer(read_only=True)

    class Meta:
        model = models.TeacherFeedback
        fields = (
            "id",
            "teacher",
            "course",
            "period",
            "rating",
            "comment",
            "anonymous",
            "tags",
            "status",
            "visibility",
            "moderation",
            "content_flags",
            "created_at",
        )
        read_only_fields = fields


class TeacherFeedbackCreateSerializer(serializers.Serializer):
    teacher_id = serializers.CharField()
    course_id = serializers.CharField()
    rating = serializers.IntegerField(min_value=1, max_value=5)
    comment = serializers.CharField(required=False, allow_blank=True, max_length=2000)
    anonymous = serializers.BooleanField(required=False, default=True)
    tags = serializers.ListField(
        child=serializers.CharField(max_length=64),
        required=False,
        allow_empty=True,
    )


class ElectiveCourseSerializer(AcademicCourseSerializer):
    department = serializers.SerializerMethodField()

    class Meta(AcademicCourseSerializer.Meta):
        fields = AcademicCourseSerializer.Meta.fields + ("department",)

    def get_department(self, obj):
        if not obj.department:
            return None
        return {"id": obj.department_id, "title": obj.department.title}


class ElectiveEnrollmentSerializer(serializers.ModelSerializer):
    course = ElectiveCourseSerializer(read_only=True)

    class Meta:
        model = models.ElectiveEnrollment
        fields = (
            "id",
            "course",
            "term",
            "status",
            "priority",
            "waitlist_position",
            "quota_snapshot",
            "enroll_window_snapshot",
            "cancel_policy",
            "conflicts",
            "links",
            "notifications",
            "timestamps",
            "created_at",
        )
        read_only_fields = fields


class ElectiveEnrollmentCreateSerializer(serializers.Serializer):
    course_id = serializers.CharField()
    term = serializers.CharField()
    priority = serializers.IntegerField(min_value=1, max_value=5, required=False)
    comment = serializers.CharField(required=False, allow_blank=True, max_length=500)
    consents = serializers.DictField(child=serializers.BooleanField())


# ---------------------------------------------------------------------------
# Сериализаторы: проекты
# ---------------------------------------------------------------------------


class ProjectVacancySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProjectVacancy
        fields = (
            "id",
            "role_code",
            "title",
            "description",
            "skills",
            "count_total",
            "count_open",
            "experience_level",
            "metadata",
        )


class ProjectSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    vacancies = ProjectVacancySerializer(many=True, read_only=True)

    class Meta:
        model = models.Project
        fields = (
            "id",
            "code",
            "status",
            "owner_type",
            "owner",
            "department",
            "title",
            "summary",
            "domain_tags",
            "skills_required",
            "format",
            "links",
            "timeline",
            "team",
            "constraints",
            "education",
            "contacts",
            "moderation",
            "metrics",
            "media",
            "vacancies",
            "created_at",
        )

    def get_owner(self, obj):
        if obj.owner_user:
            return {
                "user_id": str(obj.owner_user.id),
                "display_name": obj.owner_user.full_name or obj.owner_user.external_id,
            }
        return {"user_id": None, "display_name": None}

    def get_department(self, obj):
        if not obj.department:
            return None
        return {"id": obj.department_id, "title": obj.department.title}


class ProjectDetailSerializer(ProjectSerializer):
    class Meta(ProjectSerializer.Meta):
        fields = ProjectSerializer.Meta.fields + (
            "description_md",
            "published_at",
            "extra",
        )


class ProjectCreateSerializer(serializers.Serializer):
    title = serializers.CharField(min_length=3, max_length=120)
    summary = serializers.CharField(min_length=10, max_length=300)
    description_md = serializers.CharField(min_length=50, max_length=10000)
    owner = serializers.DictField()
    department_id = serializers.CharField(required=False, allow_blank=True)
    domain_tags = serializers.ListField(
        child=serializers.CharField(max_length=64),
        required=False,
        allow_empty=True,
    )
    skills_required = serializers.ListField(
        child=serializers.CharField(max_length=64),
        required=False,
        allow_empty=True,
    )
    links = serializers.DictField(required=False)
    timeline = serializers.DictField(required=False)
    team = serializers.DictField(required=False)
    constraints = serializers.DictField(required=False)
    education = serializers.DictField(required=False)
    contacts = serializers.DictField(required=False)


class ProjectApplicationSerializer(serializers.ModelSerializer):
    project = ProjectSerializer(read_only=True)
    vacancy = ProjectVacancySerializer(read_only=True)

    class Meta:
        model = models.ProjectApplication
        fields = (
            "id",
            "project",
            "vacancy",
            "status",
            "motivation",
            "attachments",
            "cv_url",
            "portfolio_url",
            "consents",
            "feedback",
            "created_at",
        )
        read_only_fields = fields


class ProjectApplicationCreateSerializer(serializers.Serializer):
    role_code = serializers.CharField(required=False, allow_blank=True)
    motivation = serializers.CharField(required=False, allow_blank=True, max_length=5000)
    attachments = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        allow_empty=True,
    )
    cv_url = serializers.URLField(required=False, allow_blank=True)
    portfolio_url = serializers.URLField(required=False, allow_blank=True)
    consents = serializers.DictField(child=serializers.BooleanField(), required=False)


class ProjectTeamMembershipSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = models.ProjectTeamMembership
        fields = (
            "id",
            "user",
            "role",
            "role_code",
            "responsibility",
            "joined_at",
            "left_at",
            "allocation",
            "contacts",
        )

    def get_user(self, obj):
        if not obj.user:
            return None
        return {
            "id": str(obj.user.id),
            "full_name": obj.user.full_name,
            "role": obj.user.role,
        }


class ProjectTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProjectTask
        fields = (
            "id",
            "external_id",
            "title",
            "description",
            "status",
            "assignees",
            "labels",
            "due_date",
            "tracker_payload",
        )


class ProjectSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProjectSubscription
        fields = ("id", "project", "user", "channels", "metadata", "created_at")
        read_only_fields = fields


# ---------------------------------------------------------------------------
# Сериализаторы: карьера
# ---------------------------------------------------------------------------


class CareerCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CareerCompany
        fields = (
            "id",
            "name",
            "verified_partner",
            "logo_url",
            "site_url",
            "description",
            "contacts",
            "metadata",
        )


class CareerVacancySerializer(serializers.ModelSerializer):
    company = CareerCompanySerializer(read_only=True)

    class Meta:
        model = models.CareerVacancy
        fields = (
            "id",
            "title",
            "company",
            "direction",
            "grade",
            "employment",
            "location",
            "visa_sponsorship",
            "relocation",
            "salary",
            "requirements",
            "responsibilities",
            "benefits",
            "skills",
            "experience_min_years",
            "language_requirements",
            "apply_window",
            "apply",
            "source",
            "status",
            "posted_at",
            "published_until",
            "updated_at_remote",
            "metadata",
        )


class CareerVacancyDetailSerializer(CareerVacancySerializer):
    class Meta(CareerVacancySerializer.Meta):
        fields = CareerVacancySerializer.Meta.fields


class CareerVacancyApplicationSerializer(serializers.ModelSerializer):
    vacancy = CareerVacancySerializer(read_only=True)

    class Meta:
        model = models.CareerVacancyApplication
        fields = (
            "id",
            "vacancy",
            "status",
            "resume_url",
            "cover_letter",
            "portfolio_links",
            "answers",
            "consents",
            "status_history",
            "interviews",
            "notifications",
            "created_at",
        )
        read_only_fields = fields


class CareerVacancyApplicationCreateSerializer(serializers.Serializer):
    resume_url = serializers.URLField(required=False, allow_blank=True)
    cover_letter = serializers.CharField(required=False, allow_blank=True, max_length=5000)
    portfolio_links = serializers.ListField(
        child=serializers.URLField(),
        required=False,
        allow_empty=True,
    )
    answers = serializers.DictField(required=False)
    consents = serializers.DictField(child=serializers.BooleanField(), required=False)


class CareerConsultationSerializer(serializers.ModelSerializer):
    counselor = serializers.SerializerMethodField()

    class Meta:
        model = models.CareerConsultation
        fields = (
            "id",
            "topic",
            "subtopic",
            "preferred_slots",
            "preferred_channel",
            "counselor",
            "scheduled_at",
            "duration_minutes",
            "channel_details",
            "status",
            "notes",
            "feedback",
            "created_at",
        )
        read_only_fields = fields

    def get_counselor(self, obj):
        if not obj.counselor:
            return None
        return {
            "id": str(obj.counselor.id),
            "full_name": obj.counselor.full_name,
        }


class CareerConsultationCreateSerializer(serializers.Serializer):
    topic = serializers.CharField(max_length=128)
    subtopic = serializers.CharField(required=False, allow_blank=True, max_length=128)
    preferred_slots = serializers.ListField(
        child=serializers.DictField(),
        allow_empty=True,
        required=False,
    )
    preferred_channel = serializers.CharField(required=False, allow_blank=True, max_length=64)


# ---------------------------------------------------------------------------
# Сериализаторы: деканат
# ---------------------------------------------------------------------------


class DeaneryCertificateRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DeaneryCertificateRequest
        fields = (
            "id",
            "certificate_type",
            "language",
            "purpose",
            "copies_count",
            "delivery_method",
            "pickup_location",
            "digital_copy",
            "status",
            "sla",
            "processing",
            "attachments",
            "notifications",
            "metadata",
            "created_at",
        )
        read_only_fields = fields


class DeaneryCertificateCreateSerializer(serializers.Serializer):
    certificate_type = serializers.CharField(max_length=128)
    language = serializers.CharField(required=False, allow_blank=True, max_length=32)
    purpose = serializers.CharField(required=False, allow_blank=True, max_length=255)
    copies_count = serializers.IntegerField(min_value=1, max_value=20, default=1)
    delivery_method = serializers.CharField(max_length=64)
    pickup_location = serializers.CharField(required=False, allow_blank=True, max_length=255)
    digital_copy = serializers.BooleanField(required=False, default=False)
    attachments = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        allow_empty=True,
    )


class TuitionInvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TuitionInvoice
        fields = (
            "id",
            "term",
            "amount",
            "currency",
            "due_date",
            "description",
            "status",
            "paid_at",
            "payment_method",
            "metadata",
        )


class TuitionPaymentIntentSerializer(serializers.ModelSerializer):
    invoice = TuitionInvoiceSerializer(read_only=True)

    class Meta:
        model = models.TuitionPaymentIntent
        fields = (
            "id",
            "invoice",
            "amount",
            "currency",
            "purpose",
            "status",
            "confirmation_url",
            "provider_payload",
            "metadata",
            "created_at",
        )
        read_only_fields = fields


class TuitionPaymentIntentCreateSerializer(serializers.Serializer):
    invoice_id = serializers.UUIDField(required=False)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    currency = serializers.CharField(max_length=8, default="RUB")
    purpose = serializers.CharField(required=False, allow_blank=True, max_length=128)


class DeaneryCompensationRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DeaneryCompensationRequest
        fields = (
            "id",
            "compensation_type",
            "amount",
            "currency",
            "reason",
            "bank_details",
            "documents",
            "status",
            "workflow",
            "notifications",
            "metadata",
            "created_at",
        )
        read_only_fields = fields


class DeaneryCompensationCreateSerializer(serializers.Serializer):
    compensation_type = serializers.CharField(max_length=128)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    currency = serializers.CharField(max_length=8, default="RUB")
    reason = serializers.CharField(required=False, allow_blank=True, max_length=255)
    bank_details = serializers.DictField(required=False)
    documents = serializers.ListField(child=serializers.DictField(), required=False, allow_empty=True)


class DeaneryTransferRequestSerializer(serializers.ModelSerializer):
    from_program = serializers.SerializerMethodField()
    to_program = serializers.SerializerMethodField()

    class Meta:
        model = models.DeaneryTransferRequest
        fields = (
            "id",
            "from_program",
            "to_program",
            "desired_term",
            "reason",
            "documents",
            "status",
            "workflow",
            "notifications",
            "metadata",
            "created_at",
        )
        read_only_fields = fields

    def get_from_program(self, obj):
        if not obj.from_program:
            return None
        return {"id": obj.from_program.id, "title": obj.from_program.title}

    def get_to_program(self, obj):
        if not obj.to_program:
            return None
        return {"id": obj.to_program.id, "title": obj.to_program.title}


class DeaneryTransferCreateSerializer(serializers.Serializer):
    from_program_id = serializers.CharField(required=False, allow_blank=True)
    to_program_id = serializers.CharField(required=False, allow_blank=True)
    desired_term = serializers.CharField(required=False, allow_blank=True, max_length=32)
    reason = serializers.CharField(required=False, allow_blank=True)
    documents = serializers.ListField(child=serializers.DictField(), required=False, allow_empty=True)


class AcademicLeaveRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AcademicLeaveRequest
        fields = (
            "id",
            "reason",
            "leave_from",
            "leave_to",
            "documents",
            "advisor",
            "status",
            "workflow",
            "notifications",
            "metadata",
            "created_at",
        )
        read_only_fields = fields


class AcademicLeaveCreateSerializer(serializers.Serializer):
    reason = serializers.CharField()
    leave_from = serializers.DateField()
    leave_to = serializers.DateField()
    documents = serializers.ListField(child=serializers.DictField(), required=False, allow_empty=True)
    advisor = serializers.CharField(required=False, allow_blank=True, max_length=255)


# ---------------------------------------------------------------------------
# Сериализаторы: общежитие
# ---------------------------------------------------------------------------


class DormPaymentIntentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DormPaymentIntent
        fields = (
            "id",
            "residence",
            "period",
            "amount",
            "currency",
            "status",
            "confirmation_url",
            "purpose",
            "provider_payload",
            "metadata",
            "created_at",
        )
        read_only_fields = fields


class DormPaymentIntentCreateSerializer(serializers.Serializer):
    residence = serializers.CharField(required=False, allow_blank=True, max_length=128)
    period = serializers.CharField(required=False, allow_blank=True, max_length=32)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    currency = serializers.CharField(max_length=8, default="RUB")
    purpose = serializers.CharField(required=False, allow_blank=True, max_length=128)


class DormServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DormService
        fields = (
            "id",
            "title",
            "category",
            "description",
            "price_amount",
            "price_currency",
            "delivery_time",
            "availability",
            "options",
            "required_fields",
            "metadata",
        )


class DormServiceOrderSerializer(serializers.ModelSerializer):
    service = DormServiceSerializer(read_only=True)
    payment_intent = DormPaymentIntentSerializer(read_only=True)

    class Meta:
        model = models.DormServiceOrder
        fields = (
            "id",
            "service",
            "payload",
            "status",
            "scheduled_for",
            "completed_at",
            "payment_intent",
            "notifications",
            "metadata",
            "created_at",
        )
        read_only_fields = fields


class DormServiceOrderCreateSerializer(serializers.Serializer):
    service_id = serializers.CharField()
    payload = serializers.DictField(required=False)
    scheduled_for = serializers.DateTimeField(required=False)


class DormGuestPassSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DormGuestPass
        fields = (
            "id",
            "guest_full_name",
            "guest_document",
            "visit_date",
            "visit_time_from",
            "visit_time_to",
            "notes",
            "status",
            "qr_code",
            "security_meta",
            "metadata",
            "created_at",
        )
        read_only_fields = fields


class DormGuestPassCreateSerializer(serializers.Serializer):
    guest_full_name = serializers.CharField(max_length=255)
    guest_document = serializers.DictField()
    visit_date = serializers.DateField()
    visit_time_from = serializers.TimeField(required=False, allow_null=True)
    visit_time_to = serializers.TimeField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True, max_length=255)


class DormSupportTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DormSupportTicket
        fields = (
            "id",
            "category",
            "subject",
            "description",
            "attachments",
            "status",
            "assigned_to",
            "resolution",
            "interactions",
            "metadata",
            "created_at",
        )
        read_only_fields = fields


class DormSupportTicketCreateSerializer(serializers.Serializer):
    category = serializers.CharField(max_length=128)
    subject = serializers.CharField(max_length=255)
    description = serializers.CharField()
    attachments = serializers.ListField(child=serializers.DictField(), required=False, allow_empty=True)


# ---------------------------------------------------------------------------
# Сериализаторы: внеучебные события
# ---------------------------------------------------------------------------


class CampusEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CampusEvent
        fields = (
            "id",
            "title",
            "subtitle",
            "description",
            "category",
            "starts_at",
            "ends_at",
            "location",
            "organizer",
            "cover",
            "capacity",
            "remaining",
            "registration_required",
            "registration_deadline",
            "visibility",
            "tags",
            "agenda",
            "links",
            "status",
            "meta",
        )


class EventRegistrationSerializer(serializers.ModelSerializer):
    event = CampusEventSerializer(read_only=True)

    class Meta:
        model = models.EventRegistration
        fields = (
            "id",
            "event",
            "status",
            "form_payload",
            "ticket",
            "check_ins",
            "notifications",
            "metadata",
            "created_at",
        )
        read_only_fields = fields


class EventRegistrationCreateSerializer(serializers.Serializer):
    event_id = serializers.CharField()
    form_payload = serializers.DictField(required=False)


class LibraryLoanCreateSerializer(serializers.Serializer):
    item_id = serializers.CharField()
    barcode = serializers.CharField(max_length=64, required=False, allow_blank=True)
    issued_at = serializers.DateTimeField()
    due_at = serializers.DateTimeField()
    returned_at = serializers.DateTimeField(required=False, allow_null=True)
    status = serializers.ChoiceField(choices=models.LOAN_STATUS_CHOICES, required=False)
    renewals = serializers.ListField(child=serializers.DictField(), required=False, allow_empty=True)
    fines = serializers.DictField(required=False)
    metadata = serializers.DictField(required=False)


class LibraryEBookAccessCreateSerializer(serializers.Serializer):
    item_id = serializers.CharField()
    status = serializers.ChoiceField(choices=models.EBOOK_ACCESS_STATUS_CHOICES, required=False)
    access_url = serializers.URLField(required=False, allow_blank=True)
    expires_at = serializers.DateTimeField(required=False, allow_null=True)
    device_limit = serializers.IntegerField(required=False, allow_null=True)
    drm_info = serializers.DictField(required=False)
    metadata = serializers.DictField(required=False)
    idempotency_key = serializers.CharField(max_length=64, required=False, allow_blank=True)
    request_id = serializers.CharField(max_length=64, required=False, allow_blank=True)


# ---------------------------------------------------------------------------
# Сериализаторы: библиотека
# ---------------------------------------------------------------------------


class LibraryCatalogItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.LibraryCatalogItem
        fields = (
            "id",
            "title",
            "subtitle",
            "authors",
            "publisher",
            "published_year",
            "isbn",
            "doi",
            "language",
            "media_type",
            "categories",
            "tags",
            "description",
            "cover_url",
            "formats",
            "availability",
            "rating",
            "meta",
        )


class LibraryHoldSerializer(serializers.ModelSerializer):
    item = LibraryCatalogItemSerializer(read_only=True)

    class Meta:
        model = models.LibraryHold
        fields = (
            "id",
            "item",
            "status",
            "pickup_location",
            "pickup_window",
            "expires_at",
            "notifications",
            "metadata",
            "created_at",
        )
        read_only_fields = fields


class LibraryHoldCreateSerializer(serializers.Serializer):
    item_id = serializers.CharField()
    pickup_location = serializers.CharField(max_length=255)


class LibraryLoanSerializer(serializers.ModelSerializer):
    item = LibraryCatalogItemSerializer(read_only=True)

    class Meta:
        model = models.LibraryLoan
        fields = (
            "id",
            "item",
            "barcode",
            "issued_at",
            "due_at",
            "returned_at",
            "renewals",
            "status",
            "fines",
            "metadata",
        )


class LibraryEBookAccessSerializer(serializers.ModelSerializer):
    item = LibraryCatalogItemSerializer(read_only=True)

    class Meta:
        model = models.LibraryEBookAccess
        fields = (
            "id",
            "item",
            "status",
            "access_url",
            "expires_at",
            "device_limit",
            "drm_info",
            "metadata",
            "created_at",
        )
        read_only_fields = fields


class LibraryFinePaymentIntentSerializer(serializers.ModelSerializer):
    loan = LibraryLoanSerializer(read_only=True)

    class Meta:
        model = models.LibraryFinePaymentIntent
        fields = (
            "id",
            "loan",
            "amount",
            "currency",
            "status",
            "confirmation_url",
            "provider_payload",
            "metadata",
            "created_at",
        )
        read_only_fields = fields


class LibraryFinePaymentIntentCreateSerializer(serializers.Serializer):
    loan_id = serializers.UUIDField(required=False)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField(max_length=8, default="RUB")


# ---------------------------------------------------------------------------
# Сериализаторы: сотрудники / HR
# ---------------------------------------------------------------------------


class HRTravelRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.HRTravelRequest
        fields = (
            "id",
            "title",
            "purpose",
            "destination",
            "start_date",
            "end_date",
            "transport",
            "accommodations",
            "expenses_plan",
            "approvals",
            "status",
            "documents",
            "audit",
            "metadata",
            "created_at",
        )
        read_only_fields = fields


class HRTravelRequestCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    purpose = serializers.CharField()
    destination = serializers.DictField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    transport = serializers.DictField(required=False)
    accommodations = serializers.ListField(child=serializers.DictField(), required=False, allow_empty=True)
    expenses_plan = serializers.ListField(child=serializers.DictField(), required=False, allow_empty=True)


class HRLeaveRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.HRLeaveRequest
        fields = (
            "id",
            "leave_type",
            "start_date",
            "end_date",
            "replacement",
            "approvals",
            "status",
            "notes",
            "metadata",
            "created_at",
        )
        read_only_fields = fields


class HRLeaveRequestCreateSerializer(serializers.Serializer):
    leave_type = serializers.CharField(max_length=128)
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    replacement = serializers.DictField(required=False)


class OfficeCertificateRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OfficeCertificateRequest
        fields = (
            "id",
            "certificate_type",
            "purpose",
            "delivery",
            "status",
            "metadata",
            "created_at",
        )
        read_only_fields = fields


class OfficeCertificateCreateSerializer(serializers.Serializer):
    certificate_type = serializers.CharField(max_length=128)
    purpose = serializers.CharField(required=False, allow_blank=True, max_length=255)
    delivery = serializers.DictField(required=False)


class OfficeGuestPassSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OfficeGuestPass
        fields = (
            "id",
            "guest_full_name",
            "guest_company",
            "visit_date",
            "visit_time_from",
            "visit_time_to",
            "notes",
            "status",
            "qr_payload",
            "security_meta",
            "created_at",
        )
        read_only_fields = fields


class OfficeGuestPassCreateSerializer(serializers.Serializer):
    guest_full_name = serializers.CharField(max_length=255)
    guest_company = serializers.CharField(required=False, allow_blank=True, max_length=255)
    visit_date = serializers.DateField()
    visit_time_from = serializers.TimeField(required=False, allow_null=True)
    visit_time_to = serializers.TimeField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True, max_length=255)


# ---------------------------------------------------------------------------
# Сериализаторы: дашборды руководителей и новости
# ---------------------------------------------------------------------------


class DashboardSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DashboardSnapshot
        fields = (
            "id",
            "slug",
            "date",
            "scope",
            "data",
            "generated_at",
            "source",
            "meta",
        )


class NewsMentionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.NewsMention
        fields = (
            "id",
            "query",
            "source",
            "title",
            "url",
            "excerpt",
            "published_at",
            "tonality",
            "reach",
            "metadata",
        )


# ---------------------------------------------------------------------------
# Сериализаторы: интеграции и аудит
# ---------------------------------------------------------------------------


class AccessControlEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AccessControlEvent
        fields = (
            "id",
            "device_id",
            "subject_id",
            "direction",
            "occurred_at",
            "payload",
            "processed",
            "processed_at",
            "metadata",
        )


class TrackerWebhookEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TrackerWebhookEvent
        fields = (
            "id",
            "project",
            "external_id",
            "event_type",
            "payload",
            "received_at",
            "processed_at",
            "status",
            "metadata",
        )


class PaymentProviderWebhookSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PaymentProviderWebhook
        fields = (
            "id",
            "intent_id",
            "event_type",
            "payload",
            "received_at",
            "processed_at",
            "status",
            "metadata",
        )


class MaxBotWebhookSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MaxBotWebhook
        fields = (
            "id",
            "user",
            "update_type",
            "payload",
            "received_at",
            "processed_at",
            "status",
            "metadata",
        )


class IdempotencyKeyRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.IdempotencyKeyRecord
        fields = (
            "id",
            "key",
            "scope",
            "request_hash",
            "response_payload",
            "status_code",
            "expires_at",
            "metadata",
        )


class AuditLogEntrySerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = models.AuditLogEntry
        fields = (
            "id",
            "user",
            "action",
            "resource",
            "request_id",
            "idempotency_key",
            "scope",
            "metadata",
            "ip_address",
            "user_agent",
            "performed_at",
        )

    def get_user(self, obj):
        if not obj.user:
            return None
        return {
            "id": str(obj.user.id),
            "full_name": obj.user.full_name,
            "role": obj.user.role,
        }

