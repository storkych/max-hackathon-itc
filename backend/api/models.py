import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class TimeStampedModel(models.Model):
    """Базовая абстракция c автоматическими временными метками."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDModel(TimeStampedModel):
    """Модель с UUID первичным ключом."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta(TimeStampedModel.Meta):
        abstract = True


class StringIDModel(TimeStampedModel):
    """Абстракция для сущностей со строковыми (читаемыми) идентификаторами."""

    id = models.CharField(primary_key=True, max_length=100)

    class Meta(TimeStampedModel.Meta):
        abstract = True


class UserProfile(UUIDModel):
    """Профиль пользователя MAX, основанный на init_data."""

    ROLE_APPLICANT = "applicant"
    ROLE_STUDENT = "student"
    ROLE_STAFF = "staff"
    ROLE_DEANERY = "deanery"
    ROLE_CAREER_CENTER = "career_center"
    ROLE_DORM_MANAGER = "dorm_manager"
    ROLE_LIBRARIAN = "librarian"
    ROLE_SUPERVISOR = "supervisor"
    ROLE_ADMIN = "admin"

    ROLE_CHOICES = [
        (ROLE_APPLICANT, "Applicant"),
        (ROLE_STUDENT, "Student"),
        (ROLE_STAFF, "Staff"),
        (ROLE_DEANERY, "Deanery"),
        (ROLE_CAREER_CENTER, "Career Center"),
        (ROLE_DORM_MANAGER, "Dorm Manager"),
        (ROLE_LIBRARIAN, "Librarian"),
        (ROLE_SUPERVISOR, "Supervisor"),
        (ROLE_ADMIN, "Admin"),
    ]

    user_id = models.CharField(max_length=128, unique=True)
    role = models.CharField(max_length=32, choices=ROLE_CHOICES)
    scopes = models.JSONField(default=list, blank=True)
    full_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    locale = models.CharField(max_length=32, blank=True)
    time_zone = models.CharField(max_length=64, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    academic_group = models.ForeignKey(
        "AcademicGroup",
        related_name="members",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    additional_context = models.JSONField(default=dict, blank=True)
    settings = models.JSONField(default=dict, blank=True)

    def __str__(self) -> str:
        return f"{self.full_name or self.user_id} ({self.role})"

    @property
    def is_authenticated(self) -> bool:
        """Совместимость с DRF- и Django-пермишенами."""
        return True

    @property
    def is_anonymous(self) -> bool:
        return False


# ---------------------------------------------------------------------------
# Раздел «Поступление»
# ---------------------------------------------------------------------------


class University(StringIDModel):
    """Университет из каталога поступления."""

    title = models.CharField(max_length=255)
    short_title = models.CharField(max_length=128, blank=True)
    city = models.CharField(max_length=128)
    region = models.CharField(max_length=128, blank=True)
    description = models.TextField(blank=True)

    contact_phone = models.CharField(max_length=64, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_site = models.URLField(blank=True)
    contact_address = models.CharField(max_length=255, blank=True)

    media_logo_url = models.URLField(blank=True)
    media_image_url = models.URLField(blank=True)

    stats_students_total = models.PositiveIntegerField(null=True, blank=True)
    stats_programs_count = models.PositiveIntegerField(null=True, blank=True)
    stats_budget_quota = models.PositiveIntegerField(null=True, blank=True)
    stats_employment_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        null=True,
        blank=True,
    )

    feature_has_dormitory = models.BooleanField(default=False)
    feature_has_military_department = models.BooleanField(default=False)
    feature_has_open_day = models.BooleanField(default=False)
    feature_has_preparatory_courses = models.BooleanField(default=False)
    feature_has_distance_programs = models.BooleanField(default=False)

    last_updated = models.DateTimeField(null=True, blank=True)
    data_source = models.CharField(max_length=128, blank=True)
    language = models.CharField(max_length=32, blank=True)

    extra = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["title"]

    def __str__(self) -> str:
        return self.title


class Faculty(StringIDModel):
    """Факультет/институт внутри вуза."""

    university = models.ForeignKey(
        University,
        related_name="faculties",
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255)
    short_title = models.CharField(max_length=128, blank=True)
    description = models.TextField(blank=True)
    programs_count = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        unique_together = ("university", "title")
        ordering = ["title"]

    def __str__(self) -> str:
        return f"{self.title} ({self.university_id})"


class Department(StringIDModel):
    """Кафедра/департамент для связки с программами и проектами."""

    university = models.ForeignKey(
        University,
        related_name="departments",
        on_delete=models.CASCADE,
    )
    faculty = models.ForeignKey(
        Faculty,
        related_name="departments",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ("university", "title")
        ordering = ["title"]

    def __str__(self) -> str:
        return f"{self.title} ({self.university_id})"


class Campus(UUIDModel):
    """Кампус/площадка университета."""

    university = models.ForeignKey(
        University,
        related_name="campuses",
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=128, blank=True)
    geo_lat = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )
    geo_lon = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["title"]

    def __str__(self) -> str:
        return f"{self.title} ({self.university_id})"


PROGRAM_LEVEL_BACHELOR = "bachelor"
PROGRAM_LEVEL_MASTER = "master"
PROGRAM_LEVEL_SPECIALIST = "specialist"
PROGRAM_LEVEL_PHD = "phd"

PROGRAM_LEVEL_CHOICES = [
    (PROGRAM_LEVEL_BACHELOR, "Bachelor"),
    (PROGRAM_LEVEL_MASTER, "Master"),
    (PROGRAM_LEVEL_SPECIALIST, "Specialist"),
    (PROGRAM_LEVEL_PHD, "PhD"),
]

PROGRAM_FORMAT_FULL_TIME = "full_time"
PROGRAM_FORMAT_PART_TIME = "part_time"
PROGRAM_FORMAT_DISTANCE = "distance"

PROGRAM_FORMAT_CHOICES = [
    (PROGRAM_FORMAT_FULL_TIME, "Full time"),
    (PROGRAM_FORMAT_PART_TIME, "Part time"),
    (PROGRAM_FORMAT_DISTANCE, "Distance"),
]


class Program(StringIDModel):
    """Образовательная программа."""

    university = models.ForeignKey(
        University,
        related_name="programs",
        on_delete=models.CASCADE,
    )
    department = models.ForeignKey(
        Department,
        related_name="programs",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    title = models.CharField(max_length=255)
    level = models.CharField(max_length=32, choices=PROGRAM_LEVEL_CHOICES)
    format = models.CharField(max_length=32, choices=PROGRAM_FORMAT_CHOICES)
    duration_years = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    language = models.CharField(max_length=32, blank=True)

    tuition_per_year = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )
    tuition_currency = models.CharField(max_length=8, default="RUB")
    tuition_note = models.CharField(max_length=255, blank=True)

    has_budget = models.BooleanField(default=False)
    budget_places = models.PositiveIntegerField(null=True, blank=True)
    paid_places = models.PositiveIntegerField(null=True, blank=True)
    targeted_places = models.PositiveIntegerField(null=True, blank=True)

    passing_score_last_year = models.PositiveIntegerField(null=True, blank=True)
    passing_score_median = models.PositiveIntegerField(null=True, blank=True)
    passing_score_year = models.PositiveIntegerField(null=True, blank=True)

    admission_deadline = models.DateField(null=True, blank=True)

    description = models.TextField(blank=True)
    outcomes = models.JSONField(default=list, blank=True)
    career_paths = models.JSONField(default=list, blank=True)
    links = models.JSONField(default=dict, blank=True)
    media = models.JSONField(default=dict, blank=True)
    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["title"]
        indexes = [
            models.Index(fields=["level"]),
            models.Index(fields=["format"]),
            models.Index(fields=["has_budget"]),
            models.Index(fields=["university", "department"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.university_id})"


class ProgramExam(UUIDModel):
    """Вступительный экзамен/испытание для программы."""

    program = models.ForeignKey(
        Program,
        related_name="exams",
        on_delete=models.CASCADE,
    )
    exam_type = models.CharField(max_length=32)
    subject = models.CharField(max_length=255)
    min_score = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(400)]
    )
    weight = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        null=True,
        blank=True,
    )
    priority = models.PositiveSmallIntegerField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["program", "priority", "subject"]

    def __str__(self) -> str:
        return f"{self.program_id}: {self.subject}"


class ProgramDeadline(UUIDModel):
    """Дедлайны приёмной кампании."""

    program = models.ForeignKey(
        Program,
        related_name="deadlines",
        on_delete=models.CASCADE,
    )
    phase = models.CharField(max_length=64)
    date = models.DateField()
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["date"]
        unique_together = ("program", "phase", "date")

    def __str__(self) -> str:
        return f"{self.program_id}: {self.phase} → {self.date}"


class ProgramScholarship(UUIDModel):
    """Стипендии и гранты по программе."""

    program = models.ForeignKey(
        Program,
        related_name="scholarships",
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=255)
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    currency = models.CharField(max_length=8, default="RUB")
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["program", "name"]

    def __str__(self) -> str:
        return f"{self.program_id}: {self.name}"


class ProgramAdmissionStage(UUIDModel):
    """Этапы приёмной кампании."""

    STATUS_OPEN = "open"
    STATUS_SCHEDULED = "scheduled"
    STATUS_CLOSED = "closed"

    STATUS_CHOICES = [
        (STATUS_OPEN, "Open"),
        (STATUS_SCHEDULED, "Scheduled"),
        (STATUS_CLOSED, "Closed"),
    ]

    program = models.ForeignKey(
        Program,
        related_name="admission_stages",
        on_delete=models.CASCADE,
    )
    stage = models.CharField(max_length=128)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES)
    date = models.DateField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["program", "date", "stage"]

    def __str__(self) -> str:
        return f"{self.program_id}: {self.stage}"


class ProgramFAQ(UUIDModel):
    """Частые вопросы по программе."""

    program = models.ForeignKey(
        Program,
        related_name="faq",
        on_delete=models.CASCADE,
    )
    question = models.CharField(max_length=255)
    answer = models.TextField()

    class Meta:
        ordering = ["program", "question"]

    def __str__(self) -> str:
        return f"{self.program_id}: {self.question}"


class ProgramCurriculum(TimeStampedModel):
    """Учебный план программы."""

    program = models.OneToOneField(
        Program,
        related_name="curriculum",
        on_delete=models.CASCADE,
    )
    semesters = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(20)]
    )
    core_modules = models.JSONField(default=list, blank=True)
    practice = models.JSONField(default=dict, blank=True)
    electives = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    def __str__(self) -> str:
        return f"Curriculum {self.program_id}"


class ProgramRequirement(TimeStampedModel):
    """Нормативные требования к поступлению на программу в кампанию."""

    program = models.ForeignKey(
        Program,
        related_name="requirements",
        on_delete=models.CASCADE,
    )
    year = models.PositiveIntegerField()
    regulation_url = models.URLField(blank=True)

    exams = models.JSONField(default=list, blank=True)
    additional_tests = models.JSONField(default=list, blank=True)
    thresholds = models.JSONField(default=dict, blank=True)
    tuition = models.JSONField(default=dict, blank=True)
    deadlines = models.JSONField(default=dict, blank=True)
    benefits = models.JSONField(default=dict, blank=True)
    documents = models.JSONField(default=list, blank=True)
    language_requirements = models.JSONField(default=list, blank=True)
    international = models.JSONField(default=dict, blank=True)
    application = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-year"]
        unique_together = ("program", "year")

    def __str__(self) -> str:
        return f"{self.program_id} ({self.year})"


EVENT_TYPE_OPEN_DAY = "open_day"
EVENT_TYPE_EXCURSION = "excursion"

EVENT_TYPE_CHOICES = [
    (EVENT_TYPE_OPEN_DAY, "Open day"),
    (EVENT_TYPE_EXCURSION, "Excursion"),
]


class OpenDayEvent(StringIDModel):
    """Мероприятие для абитуриентов (ДОД / экскурсия)."""

    university = models.ForeignKey(
        University,
        related_name="open_day_events",
        on_delete=models.CASCADE,
    )
    type = models.CharField(max_length=32, choices=EVENT_TYPE_CHOICES)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    date = models.DateField()
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=255)
    city = models.CharField(max_length=128, blank=True)
    capacity = models.PositiveIntegerField(null=True, blank=True)
    remaining = models.PositiveIntegerField(null=True, blank=True)
    registration_open = models.BooleanField(default=True)
    registration_deadline = models.DateTimeField(null=True, blank=True)
    media = models.JSONField(default=dict, blank=True)
    contacts = models.JSONField(default=dict, blank=True)
    links = models.JSONField(default=dict, blank=True)
    filters = models.JSONField(default=dict, blank=True)

    programs = models.ManyToManyField(
        Program,
        related_name="open_day_events",
        blank=True,
    )

    class Meta:
        ordering = ["date", "starts_at"]

    def __str__(self) -> str:
        return f"{self.title} ({self.date})"

    def decrement_remaining(self, quantity: int = 1) -> None:
        if self.capacity is None:
            return
        if self.remaining is None:
            self.remaining = max(self.capacity - quantity, 0)
        else:
            self.remaining = max(self.remaining - quantity, 0)
        self.save(update_fields=["remaining", "updated_at"])


class OpenDayRegistration(UUIDModel):
    """Регистрация абитуриента на мероприятие."""

    STATUS_REGISTERED = "registered"
    STATUS_WAITLISTED = "waitlisted"
    STATUS_CANCELED = "canceled"

    STATUS_CHOICES = [
        (STATUS_REGISTERED, "Registered"),
        (STATUS_WAITLISTED, "Waitlisted"),
        (STATUS_CANCELED, "Canceled"),
    ]

    event = models.ForeignKey(
        OpenDayEvent,
        related_name="registrations",
        on_delete=models.CASCADE,
    )
    program = models.ForeignKey(
        Program,
        related_name="open_day_registrations",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    user = models.ForeignKey(
        UserProfile,
        related_name="open_day_registrations",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    full_name = models.CharField(max_length=128)
    email = models.EmailField()
    phone = models.CharField(max_length=32, blank=True)
    comment = models.CharField(max_length=500, blank=True)

    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default=STATUS_REGISTERED)
    ticket = models.JSONField(default=dict, blank=True)
    notifications = models.JSONField(default=dict, blank=True)
    meta = models.JSONField(default=dict, blank=True)

    idempotency_key = models.CharField(max_length=64, blank=True)
    request_id = models.CharField(max_length=64, blank=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["event", "email"],
                name="unique_event_email_registration",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.event_id} → {self.email}"


class AdmissionsInquiry(UUIDModel):
    """Обращение абитуриента в приёмную комиссию."""

    TOPIC_ADMISSION = "admission"
    TOPIC_DOCUMENTS = "documents"
    TOPIC_DEADLINES = "deadlines"
    TOPIC_COST = "cost"
    TOPIC_DORM = "dorm"
    TOPIC_OTHER = "other"

    TOPIC_CHOICES = [
        (TOPIC_ADMISSION, "Admission"),
        (TOPIC_DOCUMENTS, "Documents"),
        (TOPIC_DEADLINES, "Deadlines"),
        (TOPIC_COST, "Cost"),
        (TOPIC_DORM, "Dormitory"),
        (TOPIC_OTHER, "Other"),
    ]

    STATUS_RECEIVED = "received"
    STATUS_PROCESSING = "processing"
    STATUS_ANSWERED = "answered"
    STATUS_CLOSED = "closed"

    STATUS_CHOICES = [
        (STATUS_RECEIVED, "Received"),
        (STATUS_PROCESSING, "Processing"),
        (STATUS_ANSWERED, "Answered"),
        (STATUS_CLOSED, "Closed"),
    ]

    user = models.ForeignKey(
        UserProfile,
        related_name="admissions_inquiries",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    university = models.ForeignKey(
        University,
        related_name="admissions_inquiries",
        on_delete=models.CASCADE,
    )
    program = models.ForeignKey(
        Program,
        related_name="admissions_inquiries",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    full_name = models.CharField(max_length=128)
    email = models.EmailField()
    phone = models.CharField(max_length=32, blank=True)
    question = models.TextField()
    topic = models.CharField(max_length=32, choices=TOPIC_CHOICES, default=TOPIC_OTHER)

    consents = models.JSONField(default=dict)
    attachments = models.JSONField(default=list, blank=True)
    meta = models.JSONField(default=dict, blank=True)

    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default=STATUS_RECEIVED)
    sla = models.JSONField(default=dict, blank=True)
    channels = models.JSONField(default=dict, blank=True)
    tracking = models.JSONField(default=dict, blank=True)

    idempotency_key = models.CharField(max_length=64, blank=True)
    request_id = models.CharField(max_length=64, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["university"]),
            models.Index(fields=["program"]),
            models.Index(fields=["topic"]),
        ]

    def __str__(self) -> str:
        return f"{self.full_name} → {self.university_id}"


# ---------------------------------------------------------------------------
# Раздел «Расписание и учебный процесс»
# ---------------------------------------------------------------------------


class AcademicGroup(StringIDModel):
    """Учебная группа."""

    LEVEL_BACHELOR = "bachelor"
    LEVEL_MASTER = "master"
    LEVEL_SPECIALIST = "specialist"
    LEVEL_PHD = "phd"

    EDUCATION_LEVEL_CHOICES = [
        (LEVEL_BACHELOR, "Bachelor"),
        (LEVEL_MASTER, "Master"),
        (LEVEL_SPECIALIST, "Specialist"),
        (LEVEL_PHD, "PhD"),
    ]

    university = models.ForeignKey(
        University,
        related_name="academic_groups",
        on_delete=models.CASCADE,
    )
    faculty = models.ForeignKey(
        Faculty,
        related_name="academic_groups",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    program = models.ForeignKey(
        Program,
        related_name="academic_groups",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    title = models.CharField(max_length=128)
    education_level = models.CharField(
        max_length=32,
        choices=EDUCATION_LEVEL_CHOICES,
        blank=True,
    )
    start_year = models.PositiveIntegerField(null=True, blank=True)
    curator_id = models.CharField(max_length=64, blank=True)
    schedule_time_zone = models.CharField(max_length=64, default="Europe/Moscow")
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["title"]

    def __str__(self) -> str:
        return self.title


class Teacher(StringIDModel):
    """Преподаватель."""

    full_name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=64, blank=True)
    department = models.ForeignKey(
        Department,
        related_name="teachers",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    position = models.CharField(max_length=128, blank=True)
    bio = models.TextField(blank=True)
    contacts = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["full_name"]

    def __str__(self) -> str:
        return self.full_name


class Classroom(UUIDModel):
    """Аудитория/помещение."""

    campus = models.ForeignKey(
        Campus,
        related_name="classrooms",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    name = models.CharField(max_length=64)
    building = models.CharField(max_length=128, blank=True)
    address = models.CharField(max_length=255, blank=True)
    capacity = models.PositiveIntegerField(null=True, blank=True)
    equipment = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["name"]
        unique_together = ("campus", "name")

    def __str__(self) -> str:
        return self.name


COURSE_KIND_CORE = "core"
COURSE_KIND_ELECTIVE = "elective"
COURSE_KIND_DIGITAL = "digital_faculty"

COURSE_KIND_CHOICES = [
    (COURSE_KIND_CORE, "Core"),
    (COURSE_KIND_ELECTIVE, "Elective"),
    (COURSE_KIND_DIGITAL, "Digital faculty"),
]

COURSE_FORMAT_ONLINE = "online"
COURSE_FORMAT_OFFLINE = "offline"
COURSE_FORMAT_HYBRID = "hybrid"

COURSE_FORMAT_CHOICES = [
    (COURSE_FORMAT_ONLINE, "Online"),
    (COURSE_FORMAT_OFFLINE, "Offline"),
    (COURSE_FORMAT_HYBRID, "Hybrid"),
]


class AcademicCourse(StringIDModel):
    """Учебный курс (основной или электив)."""

    kind = models.CharField(max_length=32, choices=COURSE_KIND_CHOICES, default=COURSE_KIND_CORE)
    title = models.CharField(max_length=255)
    short_title = models.CharField(max_length=128, blank=True)
    term = models.CharField(max_length=32, blank=True)
    department = models.ForeignKey(
        Department,
        related_name="courses",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    format = models.CharField(max_length=32, choices=COURSE_FORMAT_CHOICES, blank=True)
    language = models.CharField(max_length=32, blank=True)
    ects = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )
    workload_hours = models.PositiveIntegerField(null=True, blank=True)
    digital_faculty = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    schedule_preview = models.JSONField(default=list, blank=True)
    quota = models.JSONField(default=dict, blank=True)
    enroll_window = models.JSONField(default=dict, blank=True)
    prerequisites = models.JSONField(default=list, blank=True)
    anti_conflicts = models.JSONField(default=dict, blank=True)
    rating = models.JSONField(default=dict, blank=True)
    links = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    teachers = models.ManyToManyField(
        Teacher,
        related_name="courses",
        blank=True,
    )

    class Meta:
        ordering = ["title"]
        indexes = [
            models.Index(fields=["kind"]),
            models.Index(fields=["term"]),
            models.Index(fields=["format"]),
        ]

    def __str__(self) -> str:
        return self.title


LESSON_TYPE_CHOICES = [
    ("lecture", "Lecture"),
    ("seminar", "Seminar"),
    ("lab", "Lab"),
    ("exam", "Exam"),
    ("consultation", "Consultation"),
    ("other", "Other"),
]

LESSON_STATUS_SCHEDULED = "scheduled"
LESSON_STATUS_RESCHEDULED = "rescheduled"
LESSON_STATUS_CANCELED = "canceled"

LESSON_STATUS_CHOICES = [
    (LESSON_STATUS_SCHEDULED, "Scheduled"),
    (LESSON_STATUS_RESCHEDULED, "Rescheduled"),
    (LESSON_STATUS_CANCELED, "Canceled"),
]


class Lesson(StringIDModel):
    """Занятие в расписании."""

    course = models.ForeignKey(
        AcademicCourse,
        related_name="lessons",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    subject = models.CharField(max_length=255)
    lesson_type = models.CharField(max_length=32, choices=LESSON_TYPE_CHOICES)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    format = models.CharField(max_length=32, choices=COURSE_FORMAT_CHOICES, blank=True)
    room = models.ForeignKey(
        Classroom,
        related_name="lessons",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    room_snapshot = models.JSONField(default=dict, blank=True)
    teacher = models.ForeignKey(
        Teacher,
        related_name="lessons",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    teacher_snapshot = models.JSONField(default=dict, blank=True)
    group = models.ForeignKey(
        AcademicGroup,
        related_name="lessons",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    subgroup = models.JSONField(default=dict, blank=True)
    links = models.JSONField(default=dict, blank=True)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=32, choices=LESSON_STATUS_CHOICES, default=LESSON_STATUS_SCHEDULED)
    series = models.JSONField(default=dict, blank=True)
    replaces = models.JSONField(default=dict, blank=True)
    cancel_info = models.JSONField(default=dict, blank=True)
    updated_remote_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["starts_at"]
        indexes = [
            models.Index(fields=["starts_at"]),
            models.Index(fields=["ends_at"]),
            models.Index(fields=["status"]),
            models.Index(fields=["group"]),
        ]

    def __str__(self) -> str:
        return f"{self.subject} {self.starts_at}"


class TeacherFeedback(UUIDModel):
    """Отзыв о преподавателе."""

    STATUS_ACCEPTED = "accepted"
    STATUS_PENDING = "pending_moderation"
    STATUS_REJECTED = "rejected"

    STATUS_CHOICES = [
        (STATUS_ACCEPTED, "Accepted"),
        (STATUS_PENDING, "Pending moderation"),
        (STATUS_REJECTED, "Rejected"),
    ]

    user = models.ForeignKey(
        UserProfile,
        related_name="teacher_feedbacks",
        on_delete=models.CASCADE,
    )
    teacher = models.ForeignKey(
        Teacher,
        related_name="feedbacks",
        on_delete=models.CASCADE,
    )
    course = models.ForeignKey(
        AcademicCourse,
        related_name="feedbacks",
        on_delete=models.CASCADE,
    )
    period = models.CharField(max_length=32, blank=True)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    anonymous = models.BooleanField(default=True)
    tags = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default=STATUS_PENDING)
    visibility = models.JSONField(default=dict, blank=True)
    moderation = models.JSONField(default=dict, blank=True)
    content_flags = models.JSONField(default=list, blank=True)
    idempotency_key = models.CharField(max_length=64, blank=True)
    request_id = models.CharField(max_length=64, blank=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("user", "teacher", "course", "period")
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["teacher"]),
            models.Index(fields=["course"]),
        ]

    def __str__(self) -> str:
        return f"{self.teacher_id}: {self.rating}"


ENROLLMENT_STATUS_ENROLLED = "enrolled"
ENROLLMENT_STATUS_WAITLISTED = "waitlisted"
ENROLLMENT_STATUS_REJECTED = "rejected"
ENROLLMENT_STATUS_PENDING = "pending"
ENROLLMENT_STATUS_CANCELED = "canceled"

ENROLLMENT_STATUS_CHOICES = [
    (ENROLLMENT_STATUS_ENROLLED, "Enrolled"),
    (ENROLLMENT_STATUS_WAITLISTED, "Waitlisted"),
    (ENROLLMENT_STATUS_REJECTED, "Rejected"),
    (ENROLLMENT_STATUS_PENDING, "Pending"),
    (ENROLLMENT_STATUS_CANCELED, "Canceled"),
]


class ElectiveEnrollment(UUIDModel):
    """Заявка на электив/цифровую кафедру."""

    user = models.ForeignKey(
        UserProfile,
        related_name="elective_enrollments",
        on_delete=models.CASCADE,
    )
    course = models.ForeignKey(
        AcademicCourse,
        related_name="elective_enrollments",
        on_delete=models.CASCADE,
    )
    term = models.CharField(max_length=32)
    priority = models.PositiveSmallIntegerField(null=True, blank=True)
    comment = models.CharField(max_length=500, blank=True)
    consents = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=32, choices=ENROLLMENT_STATUS_CHOICES, default=ENROLLMENT_STATUS_PENDING)
    waitlist_position = models.PositiveIntegerField(null=True, blank=True)
    quota_snapshot = models.JSONField(default=dict, blank=True)
    enroll_window_snapshot = models.JSONField(default=dict, blank=True)
    cancel_policy = models.JSONField(default=dict, blank=True)
    conflicts = models.JSONField(default=list, blank=True)
    notifications = models.JSONField(default=dict, blank=True)
    links = models.JSONField(default=dict, blank=True)
    timestamps = models.JSONField(default=dict, blank=True)
    idempotency_key = models.CharField(max_length=64, blank=True)
    request_id = models.CharField(max_length=64, blank=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("user", "course", "term")
        indexes = [
            models.Index(fields=["term"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        return f"{self.user_id} → {self.course_id}"


# ---------------------------------------------------------------------------
# Раздел «Проектная деятельность»
# ---------------------------------------------------------------------------


PROJECT_OWNER_STUDENT = "student"
PROJECT_OWNER_STAFF = "staff"
PROJECT_OWNER_DEPARTMENT = "department"

PROJECT_OWNER_CHOICES = [
    (PROJECT_OWNER_STUDENT, "Student"),
    (PROJECT_OWNER_STAFF, "Staff"),
    (PROJECT_OWNER_DEPARTMENT, "Department"),
]

PROJECT_STATUS_PENDING = "pending_review"
PROJECT_STATUS_AUTO_APPROVED = "auto_approved"
PROJECT_STATUS_APPROVED = "approved"
PROJECT_STATUS_REJECTED = "rejected"
PROJECT_STATUS_DRAFT = "draft"

PROJECT_STATUS_CHOICES = [
    (PROJECT_STATUS_PENDING, "Pending review"),
    (PROJECT_STATUS_AUTO_APPROVED, "Auto approved"),
    (PROJECT_STATUS_APPROVED, "Approved"),
    (PROJECT_STATUS_REJECTED, "Rejected"),
    (PROJECT_STATUS_DRAFT, "Draft"),
]

PROJECT_FORMAT_INTRA = "intra_university"
PROJECT_FORMAT_EXTERNAL = "external_partner"
PROJECT_FORMAT_HACKATHON = "hackathon"
PROJECT_FORMAT_RESEARCH = "research"

PROJECT_FORMAT_CHOICES = [
    (PROJECT_FORMAT_INTRA, "Intra university"),
    (PROJECT_FORMAT_EXTERNAL, "External partner"),
    (PROJECT_FORMAT_HACKATHON, "Hackathon"),
    (PROJECT_FORMAT_RESEARCH, "Research"),
]


class Project(UUIDModel):
    """Инициатива/проект."""

    code = models.CharField(max_length=32, unique=True)
    owner_type = models.CharField(max_length=32, choices=PROJECT_OWNER_CHOICES)
    owner_user = models.ForeignKey(
        UserProfile,
        related_name="owned_projects",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    department = models.ForeignKey(
        Department,
        related_name="projects",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    title = models.CharField(max_length=255)
    summary = models.CharField(max_length=300)
    description_md = models.TextField()
    domain_tags = models.JSONField(default=list, blank=True)
    skills_required = models.JSONField(default=list, blank=True)
    format = models.CharField(max_length=32, choices=PROJECT_FORMAT_CHOICES, blank=True)
    links = models.JSONField(default=dict, blank=True)
    timeline = models.JSONField(default=dict, blank=True)
    team = models.JSONField(default=dict, blank=True)
    constraints = models.JSONField(default=dict, blank=True)
    education = models.JSONField(default=dict, blank=True)
    contacts = models.JSONField(default=dict, blank=True)
    moderation = models.JSONField(default=dict, blank=True)
    metrics = models.JSONField(default=dict, blank=True)
    media = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=32, choices=PROJECT_STATUS_CHOICES, default=PROJECT_STATUS_PENDING)
    published_at = models.DateTimeField(null=True, blank=True)
    extra = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["format"]),
            models.Index(fields=["owner_type"]),
        ]

    def __str__(self) -> str:
        return self.title


class ProjectVacancy(UUIDModel):
    """Вакансия/роль внутри проекта."""

    project = models.ForeignKey(
        Project,
        related_name="vacancies",
        on_delete=models.CASCADE,
    )
    role_code = models.CharField(max_length=64)
    title = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    skills = models.JSONField(default=list, blank=True)
    count_total = models.PositiveSmallIntegerField(default=1)
    count_open = models.PositiveSmallIntegerField(default=1)
    experience_level = models.CharField(max_length=64, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ("project", "role_code")

    def __str__(self) -> str:
        return f"{self.project_id}: {self.title}"


APPLICATION_STATUS_NEW = "new"
APPLICATION_STATUS_REVIEW = "under_review"
APPLICATION_STATUS_ACCEPTED = "accepted"
APPLICATION_STATUS_REJECTED = "rejected"
APPLICATION_STATUS_WITHDRAWN = "withdrawn"

APPLICATION_STATUS_CHOICES = [
    (APPLICATION_STATUS_NEW, "New"),
    (APPLICATION_STATUS_REVIEW, "Under review"),
    (APPLICATION_STATUS_ACCEPTED, "Accepted"),
    (APPLICATION_STATUS_REJECTED, "Rejected"),
    (APPLICATION_STATUS_WITHDRAWN, "Withdrawn"),
]


class ProjectApplication(UUIDModel):
    """Заявка на участие в проекте."""

    project = models.ForeignKey(
        Project,
        related_name="applications",
        on_delete=models.CASCADE,
    )
    vacancy = models.ForeignKey(
        ProjectVacancy,
        related_name="applications",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    user = models.ForeignKey(
        UserProfile,
        related_name="project_applications",
        on_delete=models.CASCADE,
    )
    motivation = models.TextField(blank=True)
    attachments = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=32, choices=APPLICATION_STATUS_CHOICES, default=APPLICATION_STATUS_NEW)
    cv_url = models.URLField(blank=True)
    portfolio_url = models.URLField(blank=True)
    consents = models.JSONField(default=dict, blank=True)
    feedback = models.JSONField(default=dict, blank=True)
    idempotency_key = models.CharField(max_length=64, blank=True)
    request_id = models.CharField(max_length=64, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("project", "user")
        indexes = [
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        return f"{self.project_id} → {self.user_id}"


class ProjectTeamMembership(UUIDModel):
    """Участник команды проекта."""

    ROLE_OWNER = "owner"
    ROLE_CURATOR = "curator"
    ROLE_MEMBER = "member"

    ROLE_CHOICES = [
        (ROLE_OWNER, "Owner"),
        (ROLE_CURATOR, "Curator"),
        (ROLE_MEMBER, "Member"),
    ]

    project = models.ForeignKey(
        Project,
        related_name="team_memberships",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        UserProfile,
        related_name="project_memberships",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    role = models.CharField(max_length=32, choices=ROLE_CHOICES, default=ROLE_MEMBER)
    role_code = models.CharField(max_length=64, blank=True)
    responsibility = models.TextField(blank=True)
    joined_at = models.DateField(null=True, blank=True)
    left_at = models.DateField(null=True, blank=True)
    allocation = models.JSONField(default=dict, blank=True)
    contacts = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ("project", "user", "role_code")

    def __str__(self) -> str:
        return f"{self.project_id}: {self.role}"


TASK_STATUS_TODO = "todo"
TASK_STATUS_IN_PROGRESS = "in_progress"
TASK_STATUS_DONE = "done"
TASK_STATUS_BLOCKED = "blocked"

TASK_STATUS_CHOICES = [
    (TASK_STATUS_TODO, "To do"),
    (TASK_STATUS_IN_PROGRESS, "In progress"),
    (TASK_STATUS_DONE, "Done"),
    (TASK_STATUS_BLOCKED, "Blocked"),
]


class ProjectTask(UUIDModel):
    """Задачи проекта (синхронизуются с трекером)."""

    project = models.ForeignKey(
        Project,
        related_name="tasks",
        on_delete=models.CASCADE,
    )
    external_id = models.CharField(max_length=128, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=32, choices=TASK_STATUS_CHOICES, default=TASK_STATUS_TODO)
    assignees = models.JSONField(default=list, blank=True)
    labels = models.JSONField(default=list, blank=True)
    due_date = models.DateField(null=True, blank=True)
    tracker_payload = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["due_date", "title"]
        unique_together = ("project", "external_id")

    def __str__(self) -> str:
        return self.title


class ProjectSubscription(UUIDModel):
    """Подписка на обновления проекта."""

    project = models.ForeignKey(
        Project,
        related_name="subscriptions",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        UserProfile,
        related_name="project_subscriptions",
        on_delete=models.CASCADE,
    )
    channels = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ("project", "user")

    def __str__(self) -> str:
        return f"{self.project_id} ← {self.user_id}"


# ---------------------------------------------------------------------------
# Раздел «Карьера»
# ---------------------------------------------------------------------------


VACANCY_STATUS_DRAFT = "draft"
VACANCY_STATUS_PENDING = "pending_review"
VACANCY_STATUS_PUBLISHED = "published"
VACANCY_STATUS_ARCHIVED = "archived"
VACANCY_STATUS_EXPIRED = "expired"

VACANCY_STATUS_CHOICES = [
    (VACANCY_STATUS_DRAFT, "Draft"),
    (VACANCY_STATUS_PENDING, "Pending review"),
    (VACANCY_STATUS_PUBLISHED, "Published"),
    (VACANCY_STATUS_ARCHIVED, "Archived"),
    (VACANCY_STATUS_EXPIRED, "Expired"),
]


class CareerCompany(StringIDModel):
    """Компания/партнёр."""

    name = models.CharField(max_length=255)
    verified_partner = models.BooleanField(default=False)
    logo_url = models.URLField(blank=True)
    site_url = models.URLField(blank=True)
    description = models.TextField(blank=True)
    contacts = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class CareerVacancy(StringIDModel):
    """Вакансия/стажировка."""

    title = models.CharField(max_length=255)
    company = models.ForeignKey(
        CareerCompany,
        related_name="vacancies",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    direction = models.JSONField(default=list, blank=True)
    grade = models.CharField(max_length=64, blank=True)
    employment = models.CharField(max_length=64, blank=True)
    location = models.JSONField(default=dict, blank=True)
    visa_sponsorship = models.BooleanField(default=False)
    relocation = models.BooleanField(default=False)
    salary = models.JSONField(default=dict, blank=True)
    requirements = models.JSONField(default=dict, blank=True)
    responsibilities = models.JSONField(default=list, blank=True)
    benefits = models.JSONField(default=list, blank=True)
    skills = models.JSONField(default=list, blank=True)
    experience_min_years = models.PositiveIntegerField(null=True, blank=True)
    language_requirements = models.JSONField(default=dict, blank=True)
    apply_window = models.JSONField(default=dict, blank=True)
    apply = models.JSONField(default=dict, blank=True)
    source = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=32, choices=VACANCY_STATUS_CHOICES, default=VACANCY_STATUS_PUBLISHED)
    posted_at = models.DateTimeField()
    published_until = models.DateTimeField(null=True, blank=True)
    updated_at_remote = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-posted_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["posted_at"]),
        ]

    def __str__(self) -> str:
        return self.title


CAREER_APPLICATION_STATUS_SUBMITTED = "submitted"
CAREER_APPLICATION_STATUS_IN_REVIEW = "in_review"
CAREER_APPLICATION_STATUS_INVITED = "invited"
CAREER_APPLICATION_STATUS_REJECTED = "rejected"
CAREER_APPLICATION_STATUS_WITHDRAWN = "withdrawn"

CAREER_APPLICATION_STATUS_CHOICES = [
    (CAREER_APPLICATION_STATUS_SUBMITTED, "Submitted"),
    (CAREER_APPLICATION_STATUS_IN_REVIEW, "In review"),
    (CAREER_APPLICATION_STATUS_INVITED, "Invited"),
    (CAREER_APPLICATION_STATUS_REJECTED, "Rejected"),
    (CAREER_APPLICATION_STATUS_WITHDRAWN, "Withdrawn"),
]


class CareerVacancyApplication(UUIDModel):
    """Отклик на вакансию."""

    vacancy = models.ForeignKey(
        CareerVacancy,
        related_name="applications",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        UserProfile,
        related_name="career_applications",
        on_delete=models.CASCADE,
    )
    resume_url = models.URLField(blank=True)
    cover_letter = models.TextField(blank=True)
    portfolio_links = models.JSONField(default=list, blank=True)
    answers = models.JSONField(default=dict, blank=True)
    consents = models.JSONField(default=dict, blank=True)
    status = models.CharField(
        max_length=32,
        choices=CAREER_APPLICATION_STATUS_CHOICES,
        default=CAREER_APPLICATION_STATUS_SUBMITTED,
    )
    status_history = models.JSONField(default=list, blank=True)
    interviews = models.JSONField(default=list, blank=True)
    notifications = models.JSONField(default=dict, blank=True)
    idempotency_key = models.CharField(max_length=64, blank=True)
    request_id = models.CharField(max_length=64, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("vacancy", "user")
        indexes = [
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        return f"{self.vacancy_id} ← {self.user_id}"


CONSULTATION_STATUS_REQUESTED = "requested"
CONSULTATION_STATUS_SCHEDULED = "scheduled"
CONSULTATION_STATUS_COMPLETED = "completed"
CONSULTATION_STATUS_CANCELLED = "cancelled"

CONSULTATION_STATUS_CHOICES = [
    (CONSULTATION_STATUS_REQUESTED, "Requested"),
    (CONSULTATION_STATUS_SCHEDULED, "Scheduled"),
    (CONSULTATION_STATUS_COMPLETED, "Completed"),
    (CONSULTATION_STATUS_CANCELLED, "Cancelled"),
]


class CareerConsultation(UUIDModel):
    """Консультации с карьерным центром."""

    user = models.ForeignKey(
        UserProfile,
        related_name="career_consultations",
        on_delete=models.CASCADE,
    )
    topic = models.CharField(max_length=128)
    subtopic = models.CharField(max_length=128, blank=True)
    preferred_slots = models.JSONField(default=list, blank=True)
    preferred_channel = models.CharField(max_length=64, blank=True)
    counselor = models.ForeignKey(
        UserProfile,
        related_name="career_consultations_as_counselor",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    scheduled_at = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    channel_details = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=32, choices=CONSULTATION_STATUS_CHOICES, default=CONSULTATION_STATUS_REQUESTED)
    notes = models.JSONField(default=dict, blank=True)
    feedback = models.JSONField(default=dict, blank=True)
    idempotency_key = models.CharField(max_length=64, blank=True)
    request_id = models.CharField(max_length=64, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.topic} ({self.user_id})"


# ---------------------------------------------------------------------------
# Раздел «Деканат»
# ---------------------------------------------------------------------------


CERTIFICATE_STATUS_SUBMITTED = "submitted"
CERTIFICATE_STATUS_IN_PROGRESS = "in_progress"
CERTIFICATE_STATUS_READY = "ready"
CERTIFICATE_STATUS_ISSUED = "issued"
CERTIFICATE_STATUS_CANCELLED = "cancelled"

CERTIFICATE_STATUS_CHOICES = [
    (CERTIFICATE_STATUS_SUBMITTED, "Submitted"),
    (CERTIFICATE_STATUS_IN_PROGRESS, "In progress"),
    (CERTIFICATE_STATUS_READY, "Ready"),
    (CERTIFICATE_STATUS_ISSUED, "Issued"),
    (CERTIFICATE_STATUS_CANCELLED, "Cancelled"),
]


class DeaneryCertificateRequest(UUIDModel):
    """Заявка на справку из деканата."""

    user = models.ForeignKey(
        UserProfile,
        related_name="certificate_requests",
        on_delete=models.CASCADE,
    )
    certificate_type = models.CharField(max_length=128)
    language = models.CharField(max_length=32, blank=True)
    purpose = models.CharField(max_length=255, blank=True)
    copies_count = models.PositiveSmallIntegerField(default=1)
    delivery_method = models.CharField(max_length=64)
    pickup_location = models.CharField(max_length=255, blank=True)
    digital_copy = models.BooleanField(default=False)
    status = models.CharField(max_length=32, choices=CERTIFICATE_STATUS_CHOICES, default=CERTIFICATE_STATUS_SUBMITTED)
    sla = models.JSONField(default=dict, blank=True)
    processing = models.JSONField(default=dict, blank=True)
    attachments = models.JSONField(default=list, blank=True)
    notifications = models.JSONField(default=dict, blank=True)
    idempotency_key = models.CharField(max_length=64, blank=True)
    request_id = models.CharField(max_length=64, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.certificate_type} ({self.user_id})"


PAYMENT_INTENT_STATUS_REQUIRES_ACTION = "requires_action"
PAYMENT_INTENT_STATUS_PROCESSING = "processing"
PAYMENT_INTENT_STATUS_SUCCEEDED = "succeeded"
PAYMENT_INTENT_STATUS_CANCELED = "canceled"

PAYMENT_INTENT_STATUS_CHOICES = [
    (PAYMENT_INTENT_STATUS_REQUIRES_ACTION, "Requires action"),
    (PAYMENT_INTENT_STATUS_PROCESSING, "Processing"),
    (PAYMENT_INTENT_STATUS_SUCCEEDED, "Succeeded"),
    (PAYMENT_INTENT_STATUS_CANCELED, "Canceled"),
]


class TuitionInvoice(UUIDModel):
    """Счёт на оплату обучения."""

    user = models.ForeignKey(
        UserProfile,
        related_name="tuition_invoices",
        on_delete=models.CASCADE,
    )
    term = models.CharField(max_length=32)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=8, default="RUB")
    due_date = models.DateField()
    description = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=32, default="pending")
    paid_at = models.DateTimeField(null=True, blank=True)
    payment_method = models.CharField(max_length=64, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["due_date"]
        indexes = [
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        return f"{self.user_id} {self.term} {self.amount}"


class TuitionPaymentIntent(UUIDModel):
    """Платёжное намерение за обучение."""

    invoice = models.ForeignKey(
        TuitionInvoice,
        related_name="payment_intents",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    user = models.ForeignKey(
        UserProfile,
        related_name="tuition_payment_intents",
        on_delete=models.CASCADE,
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=8, default="RUB")
    purpose = models.CharField(max_length=128, default="tuition")
    status = models.CharField(max_length=32, choices=PAYMENT_INTENT_STATUS_CHOICES, default=PAYMENT_INTENT_STATUS_REQUIRES_ACTION)
    confirmation_url = models.URLField(blank=True)
    provider_payload = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    idempotency_key = models.CharField(max_length=64, blank=True)
    request_id = models.CharField(max_length=64, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.user_id} {self.amount}"


COMPENSATION_STATUS_SUBMITTED = "submitted"
COMPENSATION_STATUS_IN_REVIEW = "in_review"
COMPENSATION_STATUS_APPROVED = "approved"
COMPENSATION_STATUS_REJECTED = "rejected"
COMPENSATION_STATUS_PAID = "paid"

COMPENSATION_STATUS_CHOICES = [
    (COMPENSATION_STATUS_SUBMITTED, "Submitted"),
    (COMPENSATION_STATUS_IN_REVIEW, "In review"),
    (COMPENSATION_STATUS_APPROVED, "Approved"),
    (COMPENSATION_STATUS_REJECTED, "Rejected"),
    (COMPENSATION_STATUS_PAID, "Paid"),
]


class DeaneryCompensationRequest(UUIDModel):
    """Заявка на компенсацию расходов."""

    user = models.ForeignKey(
        UserProfile,
        related_name="compensation_requests",
        on_delete=models.CASCADE,
    )
    compensation_type = models.CharField(max_length=128)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=8, default="RUB")
    reason = models.CharField(max_length=255, blank=True)
    bank_details = models.JSONField(default=dict, blank=True)
    documents = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=32, choices=COMPENSATION_STATUS_CHOICES, default=COMPENSATION_STATUS_SUBMITTED)
    workflow = models.JSONField(default=dict, blank=True)
    notifications = models.JSONField(default=dict, blank=True)
    idempotency_key = models.CharField(max_length=64, blank=True)
    request_id = models.CharField(max_length=64, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.compensation_type} {self.amount}"


TRANSFER_STATUS_SUBMITTED = "submitted"
TRANSFER_STATUS_IN_REVIEW = "in_review"
TRANSFER_STATUS_APPROVED = "approved"
TRANSFER_STATUS_REJECTED = "rejected"

TRANSFER_STATUS_CHOICES = [
    (TRANSFER_STATUS_SUBMITTED, "Submitted"),
    (TRANSFER_STATUS_IN_REVIEW, "In review"),
    (TRANSFER_STATUS_APPROVED, "Approved"),
    (TRANSFER_STATUS_REJECTED, "Rejected"),
]


class DeaneryTransferRequest(UUIDModel):
    """Заявка на перевод между программами/формами обучения."""

    user = models.ForeignKey(
        UserProfile,
        related_name="transfer_requests",
        on_delete=models.CASCADE,
    )
    from_program = models.ForeignKey(
        Program,
        related_name="transfer_requests_outgoing",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    to_program = models.ForeignKey(
        Program,
        related_name="transfer_requests_incoming",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    desired_term = models.CharField(max_length=32, blank=True)
    reason = models.TextField(blank=True)
    documents = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=32, choices=TRANSFER_STATUS_CHOICES, default=TRANSFER_STATUS_SUBMITTED)
    workflow = models.JSONField(default=dict, blank=True)
    notifications = models.JSONField(default=dict, blank=True)
    idempotency_key = models.CharField(max_length=64, blank=True)
    request_id = models.CharField(max_length=64, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.user_id} transfer"


ACADEMIC_LEAVE_STATUS_SUBMITTED = "submitted"
ACADEMIC_LEAVE_STATUS_IN_REVIEW = "in_review"
ACADEMIC_LEAVE_STATUS_APPROVED = "approved"
ACADEMIC_LEAVE_STATUS_REJECTED = "rejected"
ACADEMIC_LEAVE_STATUS_COMPLETED = "completed"

ACADEMIC_LEAVE_STATUS_CHOICES = [
    (ACADEMIC_LEAVE_STATUS_SUBMITTED, "Submitted"),
    (ACADEMIC_LEAVE_STATUS_IN_REVIEW, "In review"),
    (ACADEMIC_LEAVE_STATUS_APPROVED, "Approved"),
    (ACADEMIC_LEAVE_STATUS_REJECTED, "Rejected"),
    (ACADEMIC_LEAVE_STATUS_COMPLETED, "Completed"),
]


class AcademicLeaveRequest(UUIDModel):
    """Заявка на академический отпуск."""

    user = models.ForeignKey(
        UserProfile,
        related_name="academic_leave_requests",
        on_delete=models.CASCADE,
    )
    reason = models.TextField()
    leave_from = models.DateField()
    leave_to = models.DateField()
    documents = models.JSONField(default=list, blank=True)
    advisor = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=32, choices=ACADEMIC_LEAVE_STATUS_CHOICES, default=ACADEMIC_LEAVE_STATUS_SUBMITTED)
    workflow = models.JSONField(default=dict, blank=True)
    notifications = models.JSONField(default=dict, blank=True)
    idempotency_key = models.CharField(max_length=64, blank=True)
    request_id = models.CharField(max_length=64, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.user_id} leave {self.leave_from}"


# ---------------------------------------------------------------------------
# Раздел «Общежитие»
# ---------------------------------------------------------------------------


DORM_PAYMENT_STATUS_CHOICES = PAYMENT_INTENT_STATUS_CHOICES


class DormPaymentIntent(UUIDModel):
    """Платёжный интент за проживание в общежитии."""

    user = models.ForeignKey(
        UserProfile,
        related_name="dorm_payment_intents",
        on_delete=models.CASCADE,
    )
    residence = models.CharField(max_length=128, blank=True)
    period = models.CharField(max_length=32, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=8, default="RUB")
    status = models.CharField(max_length=32, choices=DORM_PAYMENT_STATUS_CHOICES, default=PAYMENT_INTENT_STATUS_REQUIRES_ACTION)
    confirmation_url = models.URLField(blank=True)
    purpose = models.CharField(max_length=128, default="dorm_fee")
    metadata = models.JSONField(default=dict, blank=True)
    provider_payload = models.JSONField(default=dict, blank=True)
    idempotency_key = models.CharField(max_length=64, blank=True)
    request_id = models.CharField(max_length=64, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.user_id} {self.amount}"


class DormService(StringIDModel):
    """Услуги общежития (уборка, бельё, хранение)."""

    title = models.CharField(max_length=255)
    category = models.CharField(max_length=128, blank=True)
    description = models.TextField(blank=True)
    price_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_currency = models.CharField(max_length=8, default="RUB")
    delivery_time = models.CharField(max_length=128, blank=True)
    availability = models.JSONField(default=dict, blank=True)
    options = models.JSONField(default=list, blank=True)
    required_fields = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["title"]

    def __str__(self) -> str:
        return self.title


DORM_ORDER_STATUS_SUBMITTED = "submitted"
DORM_ORDER_STATUS_CONFIRMED = "confirmed"
DORM_ORDER_STATUS_IN_PROGRESS = "in_progress"
DORM_ORDER_STATUS_COMPLETED = "completed"
DORM_ORDER_STATUS_CANCELLED = "cancelled"

DORM_ORDER_STATUS_CHOICES = [
    (DORM_ORDER_STATUS_SUBMITTED, "Submitted"),
    (DORM_ORDER_STATUS_CONFIRMED, "Confirmed"),
    (DORM_ORDER_STATUS_IN_PROGRESS, "In progress"),
    (DORM_ORDER_STATUS_COMPLETED, "Completed"),
    (DORM_ORDER_STATUS_CANCELLED, "Cancelled"),
]


class DormServiceOrder(UUIDModel):
    """Заказ услуги общежития."""

    user = models.ForeignKey(
        UserProfile,
        related_name="dorm_service_orders",
        on_delete=models.CASCADE,
    )
    service = models.ForeignKey(
        DormService,
        related_name="orders",
        on_delete=models.CASCADE,
    )
    payload = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=32, choices=DORM_ORDER_STATUS_CHOICES, default=DORM_ORDER_STATUS_SUBMITTED)
    scheduled_for = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    payment_intent = models.ForeignKey(
        DormPaymentIntent,
        related_name="service_orders",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    notifications = models.JSONField(default=dict, blank=True)
    idempotency_key = models.CharField(max_length=64, blank=True)
    request_id = models.CharField(max_length=64, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.user_id} → {self.service_id}"


GUEST_PASS_STATUS_ACTIVE = "active"
GUEST_PASS_STATUS_USED = "used"
GUEST_PASS_STATUS_CANCELLED = "cancelled"
GUEST_PASS_STATUS_EXPIRED = "expired"

GUEST_PASS_STATUS_CHOICES = [
    (GUEST_PASS_STATUS_ACTIVE, "Active"),
    (GUEST_PASS_STATUS_USED, "Used"),
    (GUEST_PASS_STATUS_CANCELLED, "Cancelled"),
    (GUEST_PASS_STATUS_EXPIRED, "Expired"),
]


class DormGuestPass(UUIDModel):
    """Гостевой пропуск в общежитие."""

    user = models.ForeignKey(
        UserProfile,
        related_name="dorm_guest_passes",
        on_delete=models.CASCADE,
    )
    guest_full_name = models.CharField(max_length=255)
    guest_document = models.JSONField(default=dict)
    visit_date = models.DateField()
    visit_time_from = models.TimeField(null=True, blank=True)
    visit_time_to = models.TimeField(null=True, blank=True)
    notes = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=32, choices=GUEST_PASS_STATUS_CHOICES, default=GUEST_PASS_STATUS_ACTIVE)
    qr_code = models.JSONField(default=dict, blank=True)
    security_meta = models.JSONField(default=dict, blank=True)
    idempotency_key = models.CharField(max_length=64, blank=True)
    request_id = models.CharField(max_length=64, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-visit_date"]

    def __str__(self) -> str:
        return f"{self.guest_full_name} {self.visit_date}"


DORM_TICKET_STATUS_OPEN = "open"
DORM_TICKET_STATUS_IN_PROGRESS = "in_progress"
DORM_TICKET_STATUS_RESOLVED = "resolved"
DORM_TICKET_STATUS_CLOSED = "closed"

DORM_TICKET_STATUS_CHOICES = [
    (DORM_TICKET_STATUS_OPEN, "Open"),
    (DORM_TICKET_STATUS_IN_PROGRESS, "In progress"),
    (DORM_TICKET_STATUS_RESOLVED, "Resolved"),
    (DORM_TICKET_STATUS_CLOSED, "Closed"),
]


class DormSupportTicket(UUIDModel):
    """Заявка в службу поддержки общежития."""

    user = models.ForeignKey(
        UserProfile,
        related_name="dorm_support_tickets",
        on_delete=models.CASCADE,
    )
    category = models.CharField(max_length=128)
    subject = models.CharField(max_length=255)
    description = models.TextField()
    attachments = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=32, choices=DORM_TICKET_STATUS_CHOICES, default=DORM_TICKET_STATUS_OPEN)
    assigned_to = models.CharField(max_length=128, blank=True)
    resolution = models.JSONField(default=dict, blank=True)
    interactions = models.JSONField(default=list, blank=True)
    idempotency_key = models.CharField(max_length=64, blank=True)
    request_id = models.CharField(max_length=64, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.subject} ({self.user_id})"


# ---------------------------------------------------------------------------
# Раздел «Внеучебные события»
# ---------------------------------------------------------------------------


EVENT_CATEGORY_CHOICES = [
    ("culture", "Culture"),
    ("sport", "Sport"),
    ("community", "Community"),
    ("education", "Education"),
    ("career", "Career"),
    ("other", "Other"),
]

EVENT_VISIBILITY_CHOICES = [
    ("public", "Public"),
    ("students_only", "Students only"),
    ("staff_only", "Staff only"),
    ("invite_only", "Invite only"),
]

EVENT_STATUS_SCHEDULED = "scheduled"
EVENT_STATUS_CANCELED = "canceled"
EVENT_STATUS_COMPLETED = "completed"

EVENT_STATUS_CHOICES = [
    (EVENT_STATUS_SCHEDULED, "Scheduled"),
    (EVENT_STATUS_CANCELED, "Canceled"),
    (EVENT_STATUS_COMPLETED, "Completed"),
]


class CampusEvent(StringIDModel):
    """Внеучебное событие."""

    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=64, choices=EVENT_CATEGORY_CHOICES, default="other")
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField(null=True, blank=True)
    location = models.JSONField(default=dict, blank=True)
    organizer = models.JSONField(default=dict, blank=True)
    cover = models.JSONField(default=dict, blank=True)
    capacity = models.PositiveIntegerField(null=True, blank=True)
    remaining = models.PositiveIntegerField(null=True, blank=True)
    registration_required = models.BooleanField(default=True)
    registration_deadline = models.DateTimeField(null=True, blank=True)
    visibility = models.CharField(max_length=32, choices=EVENT_VISIBILITY_CHOICES, default="public")
    tags = models.JSONField(default=list, blank=True)
    agenda = models.JSONField(default=list, blank=True)
    links = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=32, choices=EVENT_STATUS_CHOICES, default=EVENT_STATUS_SCHEDULED)
    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["starts_at"]

    def __str__(self) -> str:
        return self.title


EVENT_REG_STATUS_REGISTERED = "registered"
EVENT_REG_STATUS_WAITLISTED = "waitlisted"
EVENT_REG_STATUS_CANCELLED = "cancelled"
EVENT_REG_STATUS_ATTENDED = "attended"

EVENT_REG_STATUS_CHOICES = [
    (EVENT_REG_STATUS_REGISTERED, "Registered"),
    (EVENT_REG_STATUS_WAITLISTED, "Waitlisted"),
    (EVENT_REG_STATUS_CANCELLED, "Cancelled"),
    (EVENT_REG_STATUS_ATTENDED, "Attended"),
]


class EventRegistration(UUIDModel):
    """Регистрация пользователя на событие."""

    event = models.ForeignKey(
        CampusEvent,
        related_name="registrations",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        UserProfile,
        related_name="event_registrations",
        on_delete=models.CASCADE,
    )
    status = models.CharField(max_length=32, choices=EVENT_REG_STATUS_CHOICES, default=EVENT_REG_STATUS_REGISTERED)
    form_payload = models.JSONField(default=dict, blank=True)
    ticket = models.JSONField(default=dict, blank=True)
    check_ins = models.JSONField(default=list, blank=True)
    notifications = models.JSONField(default=dict, blank=True)
    idempotency_key = models.CharField(max_length=64, blank=True)
    request_id = models.CharField(max_length=64, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("event", "user")

    def __str__(self) -> str:
        return f"{self.event_id} ← {self.user_id}"


# ---------------------------------------------------------------------------
# Раздел «Библиотека»
# ---------------------------------------------------------------------------


LIBRARY_ITEM_TYPE_BOOK = "book"
LIBRARY_ITEM_TYPE_MAGAZINE = "magazine"
LIBRARY_ITEM_TYPE_EBOOK = "ebook"
LIBRARY_ITEM_TYPE_AUDIO = "audiobook"
LIBRARY_ITEM_TYPE_VIDEO = "video"

LIBRARY_ITEM_TYPE_CHOICES = [
    (LIBRARY_ITEM_TYPE_BOOK, "Book"),
    (LIBRARY_ITEM_TYPE_MAGAZINE, "Magazine"),
    (LIBRARY_ITEM_TYPE_EBOOK, "E-book"),
    (LIBRARY_ITEM_TYPE_AUDIO, "Audio"),
    (LIBRARY_ITEM_TYPE_VIDEO, "Video"),
]


class LibraryCatalogItem(StringIDModel):
    """Элемент библиотечного каталога."""

    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True)
    authors = models.JSONField(default=list, blank=True)
    publisher = models.CharField(max_length=255, blank=True)
    published_year = models.PositiveIntegerField(null=True, blank=True)
    isbn = models.CharField(max_length=32, blank=True)
    doi = models.CharField(max_length=64, blank=True)
    language = models.CharField(max_length=32, blank=True)
    media_type = models.CharField(max_length=32, choices=LIBRARY_ITEM_TYPE_CHOICES, default=LIBRARY_ITEM_TYPE_BOOK)
    categories = models.JSONField(default=list, blank=True)
    tags = models.JSONField(default=list, blank=True)
    description = models.TextField(blank=True)
    cover_url = models.URLField(blank=True)
    formats = models.JSONField(default=list, blank=True)
    availability = models.JSONField(default=dict, blank=True)
    rating = models.JSONField(default=dict, blank=True)
    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["title"]

    def __str__(self) -> str:
        return self.title


HOLD_STATUS_PLACED = "placed"
HOLD_STATUS_READY = "ready_for_pickup"
HOLD_STATUS_COLLECTED = "collected"
HOLD_STATUS_EXPIRED = "expired"
HOLD_STATUS_CANCELLED = "cancelled"

HOLD_STATUS_CHOICES = [
    (HOLD_STATUS_PLACED, "Placed"),
    (HOLD_STATUS_READY, "Ready for pickup"),
    (HOLD_STATUS_COLLECTED, "Collected"),
    (HOLD_STATUS_EXPIRED, "Expired"),
    (HOLD_STATUS_CANCELLED, "Cancelled"),
]


class LibraryHold(UUIDModel):
    """Заявка на бронирование печатного экземпляра."""

    item = models.ForeignKey(
        LibraryCatalogItem,
        related_name="holds",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        UserProfile,
        related_name="library_holds",
        on_delete=models.CASCADE,
    )
    status = models.CharField(max_length=32, choices=HOLD_STATUS_CHOICES, default=HOLD_STATUS_PLACED)
    pickup_location = models.CharField(max_length=255)
    pickup_window = models.JSONField(default=dict, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    notifications = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    idempotency_key = models.CharField(max_length=64, blank=True)
    request_id = models.CharField(max_length=64, blank=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("item", "user", "status")

    def __str__(self) -> str:
        return f"{self.item_id} ← {self.user_id}"


LOAN_STATUS_ACTIVE = "active"
LOAN_STATUS_OVERDUE = "overdue"
LOAN_STATUS_RETURNED = "returned"
LOAN_STATUS_CLOSED = "closed"

LOAN_STATUS_CHOICES = [
    (LOAN_STATUS_ACTIVE, "Active"),
    (LOAN_STATUS_OVERDUE, "Overdue"),
    (LOAN_STATUS_RETURNED, "Returned"),
    (LOAN_STATUS_CLOSED, "Closed"),
]


class LibraryLoan(UUIDModel):
    """Выдача экземпляра на руки."""

    item = models.ForeignKey(
        LibraryCatalogItem,
        related_name="loans",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        UserProfile,
        related_name="library_loans",
        on_delete=models.CASCADE,
    )
    barcode = models.CharField(max_length=64, blank=True)
    issued_at = models.DateTimeField()
    due_at = models.DateTimeField()
    returned_at = models.DateTimeField(null=True, blank=True)
    renewals = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=32, choices=LOAN_STATUS_CHOICES, default=LOAN_STATUS_ACTIVE)
    fines = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["due_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["due_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.item_id} → {self.user_id}"


EBOOK_ACCESS_STATUS_PENDING = "pending"
EBOOK_ACCESS_STATUS_ACTIVE = "active"
EBOOK_ACCESS_STATUS_EXPIRED = "expired"

EBOOK_ACCESS_STATUS_CHOICES = [
    (EBOOK_ACCESS_STATUS_PENDING, "Pending"),
    (EBOOK_ACCESS_STATUS_ACTIVE, "Active"),
    (EBOOK_ACCESS_STATUS_EXPIRED, "Expired"),
]


class LibraryEBookAccess(UUIDModel):
    """Доступ к электронному ресурсу."""

    item = models.ForeignKey(
        LibraryCatalogItem,
        related_name="ebook_accesses",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        UserProfile,
        related_name="ebook_accesses",
        on_delete=models.CASCADE,
    )
    status = models.CharField(max_length=32, choices=EBOOK_ACCESS_STATUS_CHOICES, default=EBOOK_ACCESS_STATUS_PENDING)
    access_url = models.URLField(blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    device_limit = models.PositiveSmallIntegerField(null=True, blank=True)
    drm_info = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    idempotency_key = models.CharField(max_length=64, blank=True)
    request_id = models.CharField(max_length=64, blank=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("item", "user")

    def __str__(self) -> str:
        return f"{self.item_id} ← {self.user_id}"


class LibraryFinePaymentIntent(UUIDModel):
    """Интент оплаты штрафа библиотеки."""

    user = models.ForeignKey(
        UserProfile,
        related_name="library_fine_intents",
        on_delete=models.CASCADE,
    )
    loan = models.ForeignKey(
        LibraryLoan,
        related_name="fine_intents",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=8, default="RUB")
    status = models.CharField(max_length=32, choices=PAYMENT_INTENT_STATUS_CHOICES, default=PAYMENT_INTENT_STATUS_REQUIRES_ACTION)
    confirmation_url = models.URLField(blank=True)
    provider_payload = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    idempotency_key = models.CharField(max_length=64, blank=True)
    request_id = models.CharField(max_length=64, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.user_id} fine {self.amount}"


# ---------------------------------------------------------------------------
# Раздел «Сотрудники вуза / HR»
# ---------------------------------------------------------------------------


TRAVEL_STATUS_SUBMITTED = "submitted"
TRAVEL_STATUS_APPROVED = "approved"
TRAVEL_STATUS_REJECTED = "rejected"
TRAVEL_STATUS_IN_PROGRESS = "in_progress"
TRAVEL_STATUS_COMPLETED = "completed"

TRAVEL_STATUS_CHOICES = [
    (TRAVEL_STATUS_SUBMITTED, "Submitted"),
    (TRAVEL_STATUS_APPROVED, "Approved"),
    (TRAVEL_STATUS_REJECTED, "Rejected"),
    (TRAVEL_STATUS_IN_PROGRESS, "In progress"),
    (TRAVEL_STATUS_COMPLETED, "Completed"),
]


class HRTravelRequest(UUIDModel):
    """Командировка сотрудника."""

    user = models.ForeignKey(
        UserProfile,
        related_name="travel_requests",
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255)
    purpose = models.TextField()
    destination = models.JSONField(default=dict)
    start_date = models.DateField()
    end_date = models.DateField()
    transport = models.JSONField(default=dict, blank=True)
    accommodations = models.JSONField(default=list, blank=True)
    expenses_plan = models.JSONField(default=list, blank=True)
    approvals = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=32, choices=TRAVEL_STATUS_CHOICES, default=TRAVEL_STATUS_SUBMITTED)
    documents = models.JSONField(default=list, blank=True)
    audit = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    idempotency_key = models.CharField(max_length=64, blank=True)
    request_id = models.CharField(max_length=64, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.title} ({self.user_id})"


LEAVE_STATUS_SUBMITTED = "submitted"
LEAVE_STATUS_APPROVED = "approved"
LEAVE_STATUS_REJECTED = "rejected"
LEAVE_STATUS_CANCELLED = "cancelled"

LEAVE_STATUS_CHOICES = [
    (LEAVE_STATUS_SUBMITTED, "Submitted"),
    (LEAVE_STATUS_APPROVED, "Approved"),
    (LEAVE_STATUS_REJECTED, "Rejected"),
    (LEAVE_STATUS_CANCELLED, "Cancelled"),
]


class HRLeaveRequest(UUIDModel):
    """Заявка на отпуск сотрудника."""

    user = models.ForeignKey(
        UserProfile,
        related_name="leave_requests",
        on_delete=models.CASCADE,
    )
    leave_type = models.CharField(max_length=128)
    start_date = models.DateField()
    end_date = models.DateField()
    replacement = models.JSONField(default=dict, blank=True)
    approvals = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=32, choices=LEAVE_STATUS_CHOICES, default=LEAVE_STATUS_SUBMITTED)
    notes = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    idempotency_key = models.CharField(max_length=64, blank=True)
    request_id = models.CharField(max_length=64, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.leave_type} {self.start_date}"


class OfficeCertificateRequest(UUIDModel):
    """Справка с места работы."""

    user = models.ForeignKey(
        UserProfile,
        related_name="office_certificate_requests",
        on_delete=models.CASCADE,
    )
    certificate_type = models.CharField(max_length=128)
    purpose = models.CharField(max_length=255, blank=True)
    delivery = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=32, default=CERTIFICATE_STATUS_SUBMITTED, choices=CERTIFICATE_STATUS_CHOICES)
    metadata = models.JSONField(default=dict, blank=True)
    idempotency_key = models.CharField(max_length=64, blank=True)
    request_id = models.CharField(max_length=64, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.certificate_type} ({self.user_id})"


OFFICE_GUEST_STATUS_ACTIVE = "active"
OFFICE_GUEST_STATUS_USED = "used"
OFFICE_GUEST_STATUS_CANCELLED = "cancelled"

OFFICE_GUEST_STATUS_CHOICES = [
    (OFFICE_GUEST_STATUS_ACTIVE, "Active"),
    (OFFICE_GUEST_STATUS_USED, "Used"),
    (OFFICE_GUEST_STATUS_CANCELLED, "Cancelled"),
]


class OfficeGuestPass(UUIDModel):
    """Гостевой пропуск в офис."""

    host = models.ForeignKey(
        UserProfile,
        related_name="office_guest_passes",
        on_delete=models.CASCADE,
    )
    guest_full_name = models.CharField(max_length=255)
    guest_company = models.CharField(max_length=255, blank=True)
    visit_date = models.DateField()
    visit_time_from = models.TimeField(null=True, blank=True)
    visit_time_to = models.TimeField(null=True, blank=True)
    notes = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=32, choices=OFFICE_GUEST_STATUS_CHOICES, default=OFFICE_GUEST_STATUS_ACTIVE)
    qr_payload = models.JSONField(default=dict, blank=True)
    security_meta = models.JSONField(default=dict, blank=True)
    idempotency_key = models.CharField(max_length=64, blank=True)
    request_id = models.CharField(max_length=64, blank=True)

    class Meta:
        ordering = ["-visit_date"]

    def __str__(self) -> str:
        return f"{self.guest_full_name} ({self.visit_date})"


# ---------------------------------------------------------------------------
# Раздел «Руководители / Дашборды»
# ---------------------------------------------------------------------------


class DashboardSnapshot(UUIDModel):
    """Снапшот данных для управленческих дашбордов."""

    slug = models.CharField(max_length=64)
    date = models.DateField()
    scope = models.JSONField(default=dict, blank=True)
    data = models.JSONField(default=dict)
    generated_at = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=128, blank=True)
    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ("slug", "date")
        ordering = ["-date"]

    def __str__(self) -> str:
        return f"{self.slug} {self.date}"


class NewsMention(UUIDModel):
    """Упоминание в СМИ/соцсетях."""

    query = models.CharField(max_length=255)
    source = models.CharField(max_length=128)
    title = models.CharField(max_length=255)
    url = models.URLField()
    excerpt = models.TextField(blank=True)
    published_at = models.DateTimeField()
    tonality = models.CharField(max_length=32, blank=True)
    reach = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-published_at"]
        indexes = [
            models.Index(fields=["source"]),
            models.Index(fields=["published_at"]),
        ]

    def __str__(self) -> str:
        return self.title


# ---------------------------------------------------------------------------
# Раздел «Интеграции»
# ---------------------------------------------------------------------------


class AccessControlEvent(UUIDModel):
    """Событие прохода СКУД."""

    device_id = models.CharField(max_length=64)
    subject_id = models.CharField(max_length=128)
    direction = models.CharField(max_length=16)
    occurred_at = models.DateTimeField()
    payload = models.JSONField(default=dict, blank=True)
    processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-occurred_at"]
        indexes = [
            models.Index(fields=["subject_id"]),
            models.Index(fields=["device_id"]),
        ]

    def __str__(self) -> str:
        return f"{self.subject_id} {self.occurred_at}"


class TrackerWebhookEvent(UUIDModel):
    """Входящий вебхук от таск-трекера проектов."""

    project = models.ForeignKey(
        Project,
        related_name="tracker_events",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    external_id = models.CharField(max_length=128, blank=True)
    event_type = models.CharField(max_length=64)
    payload = models.JSONField()
    received_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=32, default="pending")
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-received_at"]

    def __str__(self) -> str:
        return self.event_type


class PaymentProviderWebhook(UUIDModel):
    """Событие от платёжного провайдера."""

    intent_id = models.CharField(max_length=128, blank=True)
    event_type = models.CharField(max_length=64)
    payload = models.JSONField()
    received_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=32, default="pending")
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-received_at"]

    def __str__(self) -> str:
        return f"{self.event_type} {self.intent_id}"


class MaxBotWebhook(UUIDModel):
    """Webhook от MAX-бота."""

    user = models.ForeignKey(
        UserProfile,
        related_name="max_bot_events",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    update_type = models.CharField(max_length=64)
    payload = models.JSONField()
    received_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=32, default="pending")
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-received_at"]

    def __str__(self) -> str:
        return self.update_type


# ---------------------------------------------------------------------------
# Общие модели
# ---------------------------------------------------------------------------


class IdempotencyKeyRecord(UUIDModel):
    """Хранилище идемпотентных ключей."""

    key = models.CharField(max_length=128, unique=True)
    scope = models.CharField(max_length=128, blank=True)
    request_hash = models.CharField(max_length=128, blank=True)
    response_payload = models.JSONField(default=dict, blank=True)
    status_code = models.PositiveSmallIntegerField(null=True, blank=True)
    expires_at = models.DateTimeField()
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self) -> str:
        return self.key


class AuditLogEntry(UUIDModel):
    """Аудит действий пользователей/системы."""

    user = models.ForeignKey(
        UserProfile,
        related_name="audit_logs",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    action = models.CharField(max_length=128)
    resource = models.CharField(max_length=255, blank=True)
    request_id = models.CharField(max_length=64, blank=True)
    idempotency_key = models.CharField(max_length=128, blank=True)
    scope = models.CharField(max_length=128, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    performed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-performed_at"]
        indexes = [
            models.Index(fields=["action"]),
            models.Index(fields=["request_id"]),
        ]

    def __str__(self) -> str:
        return f"{self.action} {self.resource}"
