from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from typing import Dict, Iterable, List, Optional

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from api import models


@dataclass
class CreatedObjects:
    universities: Dict[str, models.University]
    faculties: Dict[str, models.Faculty]
    departments: Dict[str, models.Department]
    campuses: Dict[str, models.Campus]
    programs: Dict[str, models.Program]
    groups: Dict[str, models.AcademicGroup]
    teachers: Dict[str, models.Teacher]
    courses: Dict[str, models.AcademicCourse]
    classrooms: Dict[str, models.Classroom]
    users: Dict[str, models.UserProfile]
    projects: Dict[str, models.Project]
    career_vacancies: Dict[str, models.CareerVacancy]
    dorm_services: Dict[str, models.DormService]
    library_items: Dict[str, models.LibraryCatalogItem]
    hr_travel_requests: List[models.HRTravelRequest]


class DemoSeeder:
    """Генератор правдоподобных тестовых данных для всех доменов API."""

    def __init__(self, command: BaseCommand):
        self.command = command
        self.created = CreatedObjects(
            universities={},
            faculties={},
            departments={},
            campuses={},
            programs={},
            groups={},
            teachers={},
            courses={},
            classrooms={},
            users={},
            projects={},
            career_vacancies={},
            dorm_services={},
            library_items={},
            hr_travel_requests=[],
        )

    # ------------------------------------------------------------------ helpers

    def log(self, message: str) -> None:
        self.command.stdout.write(self.command.style.SUCCESS(message))

    # ---------------------------------------------------------------- universities

    def seed_universities(self) -> None:
        now = timezone.now()
        entries = [
            {
                "id": "univ-hse",
                "defaults": {
                    "title": "Национальный исследовательский университет «Высшая школа экономики»",
                    "short_title": "НИУ ВШЭ",
                    "city": "Москва",
                    "region": "Москва",
                    "description": "Ведущий российский университет в области экономики, социальных наук и IT.",
                    "contact_phone": "+7 (495) 123-45-67",
                    "contact_email": "info@hse.ru",
                    "contact_site": "https://www.hse.ru",
                    "contact_address": "101000, Москва, ул. Мясницкая, 20",
                    "media_logo_url": "https://cdn.example.com/demo/hse-logo.png",
                    "media_image_url": "https://cdn.example.com/demo/hse-campus.jpg",
                    "stats_students_total": 50000,
                    "stats_programs_count": 450,
                    "stats_budget_quota": 12000,
                    "stats_employment_rate": Decimal("92.5"),
                    "feature_has_dormitory": True,
                    "feature_has_military_department": False,
                    "feature_has_open_day": True,
                    "feature_has_preparatory_courses": True,
                    "feature_has_distance_programs": True,
                    "data_source": "demo_seed",
                    "language": "ru",
                    "extra": {"demo": True, "focus": ["digital", "economics"]},
                },
                "campuses": [
                    {
                        "key": "hse-pokrovka",
                        "title": "Кампус на Покровском бульваре",
                        "address": "Москва, Покровский бул., 11",
                        "city": "Москва",
                        "geo_lat": Decimal("55.7591"),
                        "geo_lon": Decimal("37.6440"),
                    },
                    {
                        "key": "hse-shabolovka",
                        "title": "Кампус на Шаболовке",
                        "address": "Москва, ул. Шаболовка, 26",
                        "city": "Москва",
                        "geo_lat": Decimal("55.7183"),
                        "geo_lon": Decimal("37.6086"),
                    },
                ],
                "faculties": [
                    {
                        "id": "hse-fict",
                        "title": "Факультет информатики и компьютерных технологий",
                        "short_title": "ФИКТ",
                        "description": "Подготовка специалистов в области Computer Science и программной инженерии.",
                        "programs_count": 28,
                        "departments": [
                            {
                                "id": "hse-cs-dept",
                                "title": "Департамент программной инженерии",
                                "description": "Исследования и обучение в области разработки ПО и цифровых платформ.",
                            },
                            {
                                "id": "hse-data-dept",
                                "title": "Департамент прикладного анализа данных",
                                "description": "Подготовка аналитиков данных и специалистов по машинному обучению.",
                            },
                        ],
                    }
                ],
            },
            {
                "id": "univ-itmo",
                "defaults": {
                    "title": "Университет ИТМО",
                    "short_title": "ИТМО",
                    "city": "Санкт-Петербург",
                    "region": "Санкт-Петербург",
                    "description": "Национальный исследовательский университет ИТМО — лидер в области IT и фотоники.",
                    "contact_phone": "+7 (812) 607-02-36",
                    "contact_email": "welcome@itmo.ru",
                    "contact_site": "https://itmo.ru",
                    "contact_address": "197101, Санкт-Петербург, Кронверкский пр-т, 49",
                    "media_logo_url": "https://cdn.example.com/demo/itmo-logo.png",
                    "media_image_url": "https://cdn.example.com/demo/itmo-campus.jpg",
                    "stats_students_total": 15000,
                    "stats_programs_count": 180,
                    "stats_budget_quota": 6000,
                    "stats_employment_rate": Decimal("95.3"),
                    "feature_has_dormitory": True,
                    "feature_has_military_department": False,
                    "feature_has_open_day": True,
                    "feature_has_preparatory_courses": True,
                    "feature_has_distance_programs": True,
                    "data_source": "demo_seed",
                    "language": "ru",
                    "extra": {"demo": True, "focus": ["ai", "photonics"]},
                },
                "campuses": [
                    {
                        "key": "itmo-kronverksky",
                        "title": "Главный корпус на Кронверкском проспекте",
                        "address": "Санкт-Петербург, Кронверкский пр-т, 49",
                        "city": "Санкт-Петербург",
                        "geo_lat": Decimal("59.9564"),
                        "geo_lon": Decimal("30.3085"),
                    }
                ],
                "faculties": [
                    {
                        "id": "itmo-scis",
                        "title": "Факультет программной инженерии и компьютерных технологий",
                        "short_title": "ФПИКТ",
                        "description": "Программы по искусственному интеллекту, робототехнике и киберфизическим системам.",
                        "programs_count": 22,
                        "departments": [
                            {
                                "id": "itmo-ai-dept",
                                "title": "Кафедра интеллектуальных систем",
                                "description": "Машинное обучение, компьютерное зрение и робототехника.",
                            }
                        ],
                    }
                ],
            },
            {
                "id": "univ-mgu",
                "defaults": {
                    "title": "Московский государственный университет имени М. В. Ломоносова",
                    "short_title": "МГУ",
                    "city": "Москва",
                    "region": "Москва",
                    "description": "Классический университет России с широким спектром образовательных программ и сильной научной школой.",
                    "contact_phone": "+7 (495) 939-10-00",
                    "contact_email": "info@msu.ru",
                    "contact_site": "https://www.msu.ru",
                    "contact_address": "119991, Москва, Ленинские горы, д. 1",
                    "media_logo_url": "https://cdn.example.com/demo/msu-logo.png",
                    "media_image_url": "https://cdn.example.com/demo/msu-campus.jpg",
                    "stats_students_total": 47000,
                    "stats_programs_count": 600,
                    "stats_budget_quota": 16000,
                    "stats_employment_rate": Decimal("94.1"),
                    "feature_has_dormitory": True,
                    "feature_has_military_department": True,
                    "feature_has_open_day": True,
                    "feature_has_preparatory_courses": True,
                    "feature_has_distance_programs": False,
                    "data_source": "demo_seed",
                    "language": "ru",
                    "extra": {"demo": True, "focus": ["fundamental_science", "humanities"]},
                },
                "campuses": [
                    {
                        "key": "msu-main",
                        "title": "Главное здание МГУ",
                        "address": "Москва, Ленинские горы, д. 1",
                        "city": "Москва",
                        "geo_lat": Decimal("55.7033"),
                        "geo_lon": Decimal("37.5301"),
                    },
                    {
                        "key": "msu-sparrow",
                        "title": "Кампус на Воробьёвых горах",
                        "address": "Москва, проспект Вернадского, д. 29",
                        "city": "Москва",
                        "geo_lat": Decimal("55.6955"),
                        "geo_lon": Decimal("37.5228"),
                    },
                ],
                "faculties": [
                    {
                        "id": "msu-physics",
                        "title": "Физический факультет",
                        "short_title": "ФФ",
                        "description": "Один из ведущих факультетов России в области фундаментальной и прикладной физики.",
                        "programs_count": 32,
                        "departments": [
                            {
                                "id": "msu-astro-dept",
                                "title": "Кафедра астрономии и космической физики",
                                "description": "Подготовка специалистов в области астрофизики и космических исследований.",
                            },
                            {
                                "id": "msu-quantum-dept",
                                "title": "Кафедра квантовой электроники",
                                "description": "Фундаментальные исследования в области лазерной физики и квантовых технологий.",
                            },
                        ],
                    },
                    {
                        "id": "msu-mechmath",
                        "title": "Механико-математический факультет",
                        "short_title": "МехМат",
                        "description": "Подготовка математиков и механиков мирового уровня.",
                        "programs_count": 26,
                        "departments": [
                            {
                                "id": "msu-algebra-dept",
                                "title": "Кафедра высшей алгебры",
                                "description": "Современные исследования в области алгебры и теории чисел.",
                            },
                            {
                                "id": "msu-mechanics-dept",
                                "title": "Кафедра теоретической механики",
                                "description": "Классическая и современная механика, динамика и моделирование.",
                            },
                        ],
                    },
                ],
            },
            {
                "id": "univ-spbu",
                "defaults": {
                    "title": "Санкт-Петербургский государственный университет",
                    "short_title": "СПбГУ",
                    "city": "Санкт-Петербург",
                    "region": "Санкт-Петербург",
                    "description": "Один из старейших университетов России, сочетающий фундаментальные науки и современные технологии.",
                    "contact_phone": "+7 (812) 363-60-00",
                    "contact_email": "info@spbu.ru",
                    "contact_site": "https://spbu.ru",
                    "contact_address": "199034, Санкт-Петербург, Университетская наб., 7/9",
                    "media_logo_url": "https://cdn.example.com/demo/spbu-logo.png",
                    "media_image_url": "https://cdn.example.com/demo/spbu-campus.jpg",
                    "stats_students_total": 32000,
                    "stats_programs_count": 400,
                    "stats_budget_quota": 9000,
                    "stats_employment_rate": Decimal("91.2"),
                    "feature_has_dormitory": True,
                    "feature_has_military_department": False,
                    "feature_has_open_day": True,
                    "feature_has_preparatory_courses": True,
                    "feature_has_distance_programs": True,
                    "data_source": "demo_seed",
                    "language": "ru",
                    "extra": {"demo": True, "focus": ["law", "international_relations"]},
                },
                "campuses": [
                    {
                        "key": "spbu-petrograd",
                        "title": "Петродворцовый кампус",
                        "address": "Санкт-Петербург, Петергоф, Университетский пр., 28",
                        "city": "Санкт-Петербург",
                        "geo_lat": Decimal("59.8811"),
                        "geo_lon": Decimal("29.8230"),
                    },
                    {
                        "key": "spbu-vasileostrovsky",
                        "title": "Василеостровский кампус",
                        "address": "Санкт-Петербург, Университетская наб., 7/9",
                        "city": "Санкт-Петербург",
                        "geo_lat": Decimal("59.9406"),
                        "geo_lon": Decimal("30.2969"),
                    },
                ],
                "faculties": [
                    {
                        "id": "spbu-law",
                        "title": "Юридический факультет",
                        "short_title": "ЮрФак",
                        "description": "Один из ведущих юридических факультетов страны.",
                        "programs_count": 24,
                        "departments": [
                            {
                                "id": "spbu-civil-dept",
                                "title": "Кафедра гражданского права",
                                "description": "Исследования и преподавание в области гражданского и корпоративного права.",
                            },
                            {
                                "id": "spbu-international-law",
                                "title": "Кафедра международного публичного права",
                                "description": "Подготовка специалистов по международному праву и дипломатии.",
                            },
                        ],
                    },
                    {
                        "id": "spbu-math-mech",
                        "title": "Математико-механический факультет",
                        "short_title": "МатМех",
                        "description": "Фундаментальная подготовка в области математики, механики и информатики.",
                        "programs_count": 20,
                        "departments": [
                            {
                                "id": "spbu-applied-math",
                                "title": "Кафедра прикладной математики и информатики",
                                "description": "Разработка алгоритмов, моделирование и анализ данных.",
                            },
                            {
                                "id": "spbu-control-systems",
                                "title": "Кафедра систем управления",
                                "description": "Исследования в области автоматизированных систем управления и робототехники.",
                            },
                        ],
                    },
                ],
            },
            {
                "id": "univ-mipt",
                "defaults": {
                    "title": "Московский физико-технический институт",
                    "short_title": "МФТИ",
                    "city": "Долгопрудный",
                    "region": "Московская область",
                    "description": "Институт, ориентированный на подготовку инженеров и исследователей в области физики, математики и современного ИТ.",
                    "contact_phone": "+7 (495) 408-45-54",
                    "contact_email": "admission@mipt.ru",
                    "contact_site": "https://mipt.ru",
                    "contact_address": "141701, Московская область, г. Долгопрудный, Институтский пер., 9",
                    "media_logo_url": "https://cdn.example.com/demo/mipt-logo.png",
                    "media_image_url": "https://cdn.example.com/demo/mipt-campus.jpg",
                    "stats_students_total": 8000,
                    "stats_programs_count": 120,
                    "stats_budget_quota": 3000,
                    "stats_employment_rate": Decimal("97.8"),
                    "feature_has_dormitory": True,
                    "feature_has_military_department": False,
                    "feature_has_open_day": True,
                    "feature_has_preparatory_courses": True,
                    "feature_has_distance_programs": True,
                    "data_source": "demo_seed",
                    "language": "ru",
                    "extra": {"demo": True, "focus": ["physics", "engineering", "computer_science"]},
                },
                "campuses": [
                    {
                        "key": "mipt-main",
                        "title": "Главный кампус МФТИ",
                        "address": "Долгопрудный, Институтский пер., 9",
                        "city": "Долгопрудный",
                        "geo_lat": Decimal("55.9294"),
                        "geo_lon": Decimal("37.5215"),
                    }
                ],
                "faculties": [
                    {
                        "id": "mipt-phystech",
                        "title": "Физтех-школа прикладной математики и информатики",
                        "short_title": "ФПМИ",
                        "description": "Лидеры в области прикладной математики, анализа данных и машинного обучения.",
                        "programs_count": 18,
                        "departments": [
                            {
                                "id": "mipt-ml-dept",
                                "title": "Кафедра машинного обучения",
                                "description": "Алгоритмы машинного обучения, глубокие нейронные сети и приложения в индустрии.",
                            },
                            {
                                "id": "mipt-programming-dept",
                                "title": "Кафедра программной инженерии",
                                "description": "Разработка высоконагруженных систем, DevOps и распределённые сервисы.",
                            },
                        ],
                    },
                    {
                        "id": "mipt-aero",
                        "title": "Физтех-школа аэрокосмических технологий",
                        "short_title": "ФШАТ",
                        "description": "Подготовка инженеров для авиа- и космической отрасли совместно с ведущими предприятиями.",
                        "programs_count": 15,
                        "departments": [
                            {
                                "id": "mipt-aerodynamics",
                                "title": "Кафедра аэродинамики и летательных аппаратов",
                                "description": "Аэродинамика, композитные материалы и расчёт летательных аппаратов.",
                            },
                            {
                                "id": "mipt-space-systems",
                                "title": "Кафедра космических систем",
                                "description": "Проектирование спутников, систем связи и космических аппаратов.",
                            },
                        ],
                    },
                ],
            },
        ]

        for entry in entries:
            defaults = {**entry["defaults"], "last_updated": now}
            university, _ = models.University.objects.update_or_create(
                id=entry["id"],
                defaults=defaults,
            )
            university.extra.setdefault("demo", True)
            university.save(update_fields=["extra", "updated_at"])
            self.created.universities[entry["id"]] = university

            for campus_entry in entry.get("campuses", []):
                campus_defaults = {
                    "title": campus_entry["title"],
                    "address": campus_entry.get("address", ""),
                    "city": campus_entry.get("city", ""),
                    "geo_lat": campus_entry.get("geo_lat"),
                    "geo_lon": campus_entry.get("geo_lon"),
                    "metadata": {"demo": True},
                }
                campus, _ = models.Campus.objects.update_or_create(
                    university=university,
                    title=campus_defaults["title"],
                    defaults=campus_defaults,
                )
                self.created.campuses[campus_entry["key"]] = campus

            for faculty_entry in entry.get("faculties", []):
                faculty, _ = models.Faculty.objects.update_or_create(
                    id=faculty_entry["id"],
                    defaults={
                        "university": university,
                        "title": faculty_entry["title"],
                        "short_title": faculty_entry.get("short_title", ""),
                        "description": faculty_entry.get("description", ""),
                        "programs_count": faculty_entry.get("programs_count"),
                    },
                )
                self.created.faculties[faculty.id] = faculty

                for dept_entry in faculty_entry.get("departments", []):
                    dept, _ = models.Department.objects.update_or_create(
                        id=dept_entry["id"],
                        defaults={
                            "university": university,
                            "faculty": faculty,
                            "title": dept_entry["title"],
                            "description": dept_entry.get("description", ""),
                        },
                    )
                    self.created.departments[dept.id] = dept

        self.log("✓ Университеты, кампусы, факультеты и департаменты готовы")

    # -------------------------------------------------------------------- programs

    def seed_programs(self) -> None:
        program_entries = [
            {
                "id": "prog-hse-se",
                "university": "univ-hse",
                "department": "hse-cs-dept",
                "title": "Программная инженерия",
                "level": models.PROGRAM_LEVEL_BACHELOR,
                "format": models.PROGRAM_FORMAT_FULL_TIME,
                "duration_years": 4,
                "language": "ru",
                "tuition_per_year": Decimal("360000.00"),
                "has_budget": True,
                "budget_places": 80,
                "paid_places": 40,
                "targeted_places": 10,
                "passing_score_last_year": 287,
                "passing_score_median": 275,
                "passing_score_year": 2023,
                "admission_deadline": date.today().replace(month=7, day=25),
                "description": "Базовая программа по разработке программного обеспечения и системному анализу.",
                "career_paths": [
                    "Разработчик программного обеспечения",
                    "Системный архитектор",
                    "Инженер по качеству",
                ],
                "links": {"brochure": "https://www.hse.ru/ba/se"},
            },
            {
                "id": "prog-hse-data",
                "university": "univ-hse",
                "department": "hse-data-dept",
                "title": "Прикладной анализ данных",
                "level": models.PROGRAM_LEVEL_MASTER,
                "format": models.PROGRAM_FORMAT_FULL_TIME,
                "duration_years": 2,
                "language": "ru",
                "tuition_per_year": Decimal("420000.00"),
                "has_budget": True,
                "budget_places": 30,
                "paid_places": 20,
                "targeted_places": 5,
                "passing_score_last_year": 89,
                "passing_score_median": 85,
                "passing_score_year": 2023,
                "admission_deadline": date.today().replace(month=8, day=10),
                "description": "Подготовка аналитиков данных и специалистов по машинному обучению.",
                "career_paths": [
                    "Data Scientist",
                    "ML Engineer",
                    "BI-аналитик",
                ],
                "links": {"landing": "https://www.hse.ru/ma/datasci"},
            },
            {
                "id": "prog-itmo-robotics",
                "university": "univ-itmo",
                "department": "itmo-ai-dept",
                "title": "Интеллектуальная робототехника",
                "level": models.PROGRAM_LEVEL_MASTER,
                "format": models.PROGRAM_FORMAT_FULL_TIME,
                "duration_years": 2,
                "language": "en",
                "tuition_per_year": Decimal("450000.00"),
                "has_budget": True,
                "budget_places": 25,
                "paid_places": 35,
                "targeted_places": 5,
                "passing_score_last_year": 91,
                "passing_score_median": 88,
                "passing_score_year": 2023,
                "admission_deadline": date.today().replace(month=8, day=15),
                "description": "Программа по разработке автономных робототехнических систем.",
                "career_paths": [
                    "Robotics Engineer",
                    "Computer Vision Engineer",
                ],
                "links": {"landing": "https://en.itmo.ru/en/page/135/"},
            },
            {
                "id": "prog-msu-astro",
                "university": "univ-mgu",
                "department": "msu-astro-dept",
                "title": "Астрофизика и космические исследования",
                "level": models.PROGRAM_LEVEL_MASTER,
                "format": models.PROGRAM_FORMAT_PART_TIME,
                "duration_years": 2,
                "language": "ru",
                "tuition_per_year": Decimal("390000.00"),
                "has_budget": True,
                "budget_places": 18,
                "paid_places": 22,
                "targeted_places": 4,
                "passing_score_last_year": 93,
                "passing_score_median": 90,
                "passing_score_year": 2023,
                "admission_deadline": date.today().replace(month=7, day=30),
                "description": "Программа для исследователей, занимающихся астрофизикой и космическими миссиями.",
                "career_paths": [
                    "Астрофизик",
                    "Специалист по космическим данным",
                    "Инженер космических наблюдений",
                ],
                "links": {"landing": "https://www.msu.ru/astro"},
            },
            {
                "id": "prog-spbu-law",
                "university": "univ-spbu",
                "department": "spbu-civil-dept",
                "title": "Международное коммерческое право",
                "level": models.PROGRAM_LEVEL_MASTER,
                "format": models.PROGRAM_FORMAT_FULL_TIME,
                "duration_years": 2,
                "language": "ru",
                "tuition_per_year": Decimal("310000.00"),
                "has_budget": False,
                "budget_places": 0,
                "paid_places": 40,
                "targeted_places": 10,
                "passing_score_last_year": 82,
                "passing_score_median": 79,
                "passing_score_year": 2023,
                "admission_deadline": date.today().replace(month=8, day=25),
                "description": "Фокус на международном праве, арбитражах и сопровождении сделок.",
                "career_paths": [
                    "Юрист международного права",
                    "Корпоративный юрист",
                ],
                "links": {"landing": "https://law.spbu.ru/intl-commerce"},
            },
            {
                "id": "prog-hse-digital",
                "university": "univ-hse",
                "department": "hse-cs-dept",
                "title": "Цифровые сервисы и продуктовая аналитика",
                "level": models.PROGRAM_LEVEL_BACHELOR,
                "format": models.PROGRAM_FORMAT_DISTANCE,
                "duration_years": 4,
                "language": "ru",
                "tuition_per_year": Decimal("280000.00"),
                "has_budget": False,
                "budget_places": 0,
                "paid_places": 75,
                "targeted_places": 0,
                "passing_score_last_year": 265,
                "passing_score_median": 250,
                "passing_score_year": 2023,
                "admission_deadline": date.today().replace(month=7, day=15),
                "description": "Онлайн-программа по разработке и аналитике цифровых продуктов.",
                "career_paths": [
                    "Продуктовый аналитик",
                    "Digital Project Manager",
                    "Growth-аналитик",
                ],
                "links": {"landing": "https://www.hse.ru/digital-services"},
            },
        ]

        for entry in program_entries:
            university = self.created.universities[entry["university"]]
            department = self.created.departments.get(entry["department"])
            program, _ = models.Program.objects.update_or_create(
                id=entry["id"],
                defaults={
                    "university": university,
                    "department": department,
                    "title": entry["title"],
                    "level": entry["level"],
                    "format": entry["format"],
                    "duration_years": entry["duration_years"],
                    "language": entry["language"],
                    "tuition_per_year": entry["tuition_per_year"],
                    "has_budget": entry["has_budget"],
                    "budget_places": entry["budget_places"],
                    "paid_places": entry["paid_places"],
                    "targeted_places": entry["targeted_places"],
                    "passing_score_last_year": entry["passing_score_last_year"],
                    "passing_score_median": entry["passing_score_median"],
                    "passing_score_year": entry["passing_score_year"],
                    "admission_deadline": entry["admission_deadline"],
                    "description": entry["description"],
                    "career_paths": entry["career_paths"],
                    "links": entry["links"],
                    "media": {"demo": True},
                    "meta": {"demo": True},
                },
            )
            self.created.programs[program.id] = program

            models.ProgramRequirement.objects.update_or_create(
                program=program,
                year=2024,
                defaults={
                    "regulation_url": "https://www.example.com/docs/regulations.pdf",
                    "exams": [
                        {"subject": "Информатика", "min_score": 75},
                        {"subject": "Математика", "min_score": 70},
                        {"subject": "Русский язык", "min_score": 68},
                    ],
                    "thresholds": {
                        "budget": 280,
                        "paid": 240,
                    },
                    "tuition": {
                        "per_year": str(entry["tuition_per_year"]),
                        "currency": "RUB",
                    },
                    "deadlines": {
                        "documents": "2024-07-20",
                        "exams": "2024-07-05",
                    },
                    "benefits": {"olympiad": "Победители получают 100 баллов"},
                    "documents": [
                        {"title": "Паспорт"},
                        {"title": "Аттестат"},
                    ],
                    "language_requirements": [
                        {"exam": "IELTS 6.0", "required": False},
                    ],
                    "international": {"support": True},
                    "application": {"portal": "https://apply.example.com"},
                    "metadata": {"demo": True},
                },
            )

        self.log("✓ Программы, требования и базовые справочники созданы")

    # ---------------------------------------------------------------- admissions

    def seed_open_days_and_inquiries(self) -> None:
        now = timezone.now()
        events = [
            {
                "id": "hse-open-day-july",
                "university": "univ-hse",
                "title": "День открытых дверей на Покровке",
                "city": "Москва",
                "location": "Москва, Покровский бул., 11",
                "programs": ["prog-hse-se", "prog-hse-data"],
                "starts_at": now + timedelta(days=10),
                "duration_hours": 3,
                "capacity": 150,
                "filters": {"format": "offline", "level": "bachelor"},
            },
            {
                "id": "itmo-open-day-august",
                "university": "univ-itmo",
                "title": "Презентация магистратуры по робототехнике",
                "city": "Санкт-Петербург",
                "location": "Кронверкский пр-т, 49",
                "programs": ["prog-itmo-robotics"],
                "starts_at": now + timedelta(days=20),
                "duration_hours": 2,
                "capacity": 120,
                "filters": {"format": "hybrid", "language": "en"},
            },
            {
                "id": "msu-astro-tour",
                "university": "univ-mgu",
                "title": "Экскурсия в астрономическую обсерваторию",
                "city": "Москва",
                "location": "Москва, Ленинские горы, д. 1, обсерватория",
                "programs": ["prog-msu-astro"],
                "starts_at": now + timedelta(days=25),
                "duration_hours": 2,
                "capacity": 30,
                "type": models.EVENT_TYPE_EXCURSION,
                "filters": {"format": "offline", "audience": "masters"},
                "registration_open": False,
                "remaining": 6,
            },
            {
                "id": "spbu-law-open-day-online",
                "university": "univ-spbu",
                "title": "Онлайн-встреча по международному коммерческому праву",
                "city": "Санкт-Петербург",
                "location": "Онлайн",
                "programs": ["prog-spbu-law"],
                "starts_at": now + timedelta(days=5),
                "duration_hours": 1,
                "capacity": 250,
                "filters": {"format": "online", "language": "ru"},
            },
        ]

        for event_data in events:
            university = self.created.universities[event_data["university"]]
            starts_at = event_data["starts_at"]
            ends_at = starts_at + timedelta(hours=event_data["duration_hours"])
            registration_deadline = starts_at - timedelta(days=2)
            event_type = event_data.get("type", models.EVENT_TYPE_OPEN_DAY)
            description = event_data.get(
                "description",
                "Знакомство с программами, встречи с преподавателями, экскурсия по кампусу.",
            )
            filters = event_data.get("filters", {"format": "offline"})
            registration_open = event_data.get("registration_open", True)
            remaining = event_data.get("remaining", event_data["capacity"])
            event, _ = models.OpenDayEvent.objects.update_or_create(
                id=event_data["id"],
                defaults={
                    "university": university,
                    "type": event_type,
                    "title": event_data["title"],
                    "description": description,
                    "date": starts_at.date(),
                    "starts_at": starts_at,
                    "ends_at": ends_at,
                    "location": event_data["location"],
                    "city": event_data["city"],
                    "capacity": event_data["capacity"],
                    "remaining": remaining,
                    "registration_open": registration_open,
                    "registration_deadline": registration_deadline,
                    "media": {"poster_url": "https://cdn.example.com/demo/openday.jpg"},
                    "contacts": {"email": "admissions@" + university.contact_site.split("//")[-1]},
                    "links": {"registration": "https://apply.example.com/events"},
                    "filters": filters,
                },
            )
            program_objects = [self.created.programs[pid] for pid in event_data["programs"]]
            event.programs.set(program_objects)

        student = self.created.users.get("student")
        applicant = self.created.users.get("applicant")
        registration_entries = []
        if student:
            registration_entries.append(
                {
                    "event_id": "hse-open-day-july",
                    "program_id": "prog-hse-se",
                    "user": student,
                    "email": "max@example.com",
                    "full_name": student.full_name or "Максим Иванов",
                    "phone": "+7 (999) 000-00-00",
                    "status": models.EVENT_REG_STATUS_REGISTERED,
                    "ticket": {"format": "qr", "code": "HSE-OPEN-QR"},
                    "comment": "Планирую приехать с родителями",
                }
            )
        if applicant:
            registration_entries.append(
                {
                    "event_id": "spbu-law-open-day-online",
                    "program_id": "prog-spbu-law",
                    "user": applicant,
                    "email": "anna.applicant@example.com",
                    "full_name": applicant.full_name or "Анна Заявкина",
                    "phone": "+7 (921) 100-20-30",
                    "status": models.EVENT_REG_STATUS_WAITLISTED,
                    "ticket": {"format": "pdf", "code": "SPBU-LAW-2024"},
                    "comment": "Хочу узнать о стажировках",
                }
            )

        for entry in registration_entries:
            event = models.OpenDayEvent.objects.get(id=entry["event_id"])
            program = self.created.programs[entry["program_id"]]
            models.OpenDayRegistration.objects.update_or_create(
                event=event,
                email=entry["email"],
                defaults={
                    "program": program,
                    "user": entry["user"],
                    "full_name": entry["full_name"],
                    "phone": entry["phone"],
                    "comment": entry["comment"],
                    "status": entry["status"],
                    "ticket": entry["ticket"],
                    "meta": {"demo": True},
                },
            )

        inquiries = []
        if student:
            inquiries.append(
                {
                    "user": student,
                    "university": "univ-hse",
                    "program": "prog-hse-se",
                    "question": "Какие вступительные испытания необходимы и когда ждать результаты?",
                    "topic": models.AdmissionsInquiry.TOPIC_ADMISSION,
                    "status": models.AdmissionsInquiry.STATUS_PROCESSING,
                    "email": "max@example.com",
                    "phone": "+7 (999) 000-00-00",
                }
            )
        if applicant:
            inquiries.append(
                {
                    "user": applicant,
                    "university": "univ-spbu",
                    "program": "prog-spbu-law",
                    "question": "Нужны ли нотариально заверенные переводы диплома для подачи?",
                    "topic": models.AdmissionsInquiry.TOPIC_DOCUMENTS,
                    "status": models.AdmissionsInquiry.STATUS_RECEIVED,
                    "email": "anna.applicant@example.com",
                    "phone": "+7 (921) 100-20-30",
                }
            )
            inquiries.append(
                {
                    "user": applicant,
                    "university": "univ-mgu",
                    "program": "prog-msu-astro",
                    "question": "Можно ли получить общежитие на время обучения?",
                    "topic": models.AdmissionsInquiry.TOPIC_OTHER,
                    "status": models.AdmissionsInquiry.STATUS_ANSWERED,
                    "email": "anna.applicant@example.com",
                    "phone": "+7 (921) 100-20-30",
                }
            )

        for entry in inquiries:
            models.AdmissionsInquiry.objects.update_or_create(
                user=entry["user"],
                university=self.created.universities[entry["university"]],
                program=self.created.programs[entry["program"]],
                question=entry["question"],
                defaults={
                    "full_name": entry["user"].full_name or entry["user"].user_id,
                    "email": entry["email"],
                    "phone": entry["phone"],
                    "topic": entry["topic"],
                    "consents": {"personal_data": True},
                    "attachments": [],
                    "meta": {"source": "demo_seed"},
                    "status": entry["status"],
                    "channels": {"email": entry["email"]},
                    "tracking": {"crm": {"enabled": True}},
                },
            )

        self.log("✓ События для абитуриентов и обращения созданы")

    # -------------------------------------------------------------- academic part

    def seed_academic_groups(self) -> None:
        group_entries = [
            {
                "id": "CS-101",
                "university": "univ-hse",
                "program": "prog-hse-se",
                "title": "БПИ-201",
                "education_level": models.AcademicGroup.LEVEL_BACHELOR,
                "start_year": 2023,
            },
            {
                "id": "AI-202",
                "university": "univ-itmo",
                "program": "prog-itmo-robotics",
                "title": "МАИ-2022",
                "education_level": models.AcademicGroup.LEVEL_MASTER,
                "start_year": 2022,
            },
            {
                "id": "PHYS-401",
                "university": "univ-mgu",
                "program": "prog-msu-astro",
                "title": "МАФ-2023",
                "education_level": models.AcademicGroup.LEVEL_MASTER,
                "start_year": 2023,
            },
            {
                "id": "LAW-101",
                "university": "univ-spbu",
                "program": "prog-spbu-law",
                "title": "МЮК-2024",
                "education_level": models.AcademicGroup.LEVEL_MASTER,
                "start_year": 2024,
            },
            {
                "id": "DIGI-001",
                "university": "univ-hse",
                "program": "prog-hse-digital",
                "title": "ЦСА-2024",
                "education_level": models.AcademicGroup.LEVEL_BACHELOR,
                "start_year": 2024,
            },
        ]

        for entry in group_entries:
            university = self.created.universities[entry["university"]]
            program = self.created.programs.get(entry["program"])
            faculty = None
            if program and program.department_id:
                dept = self.created.departments.get(program.department_id)
                faculty = dept.faculty if dept else None
            group, _ = models.AcademicGroup.objects.update_or_create(
                id=entry["id"],
                defaults={
                    "university": university,
                    "faculty": faculty,
                    "program": program,
                    "title": entry["title"],
                    "education_level": entry["education_level"],
                    "start_year": entry["start_year"],
                    "schedule_time_zone": "Europe/Moscow",
                    "metadata": {"demo": True},
                },
            )
            self.created.groups[group.id] = group

        self.log("✓ Учебные группы добавлены")

    def seed_teachers_courses_and_lessons(self) -> None:
        teacher_entries = [
            {
                "id": "teacher-petrov",
                "full_name": "Сергей Петров",
                "email": "s.petrov@hse.ru",
                "department": "hse-cs-dept",
                "position": "Доцент",
            },
            {
                "id": "teacher-smirnova",
                "full_name": "Анна Смирнова",
                "email": "a.smirnova@itmo.ru",
                "department": "itmo-ai-dept",
                "position": "Профессор",
            },
            {
                "id": "teacher-ivanova",
                "full_name": "Мария Иванова",
                "email": "m.ivanova@msu.ru",
                "department": "msu-astro-dept",
                "position": "Профессор",
            },
            {
                "id": "teacher-orlov",
                "full_name": "Дмитрий Орлов",
                "email": "d.orlov@spbu.ru",
                "department": "spbu-civil-dept",
                "position": "Доцент",
            },
        ]

        for entry in teacher_entries:
            department = self.created.departments.get(entry["department"])
            teacher, _ = models.Teacher.objects.update_or_create(
                id=entry["id"],
                defaults={
                    "full_name": entry["full_name"],
                    "email": entry["email"],
                    "phone": "+7 (812) 555-55-55",
                    "department": department,
                    "position": entry["position"],
                    "bio": "Преподаватель с многолетним опытом в индустрии и академии.",
                    "contacts": {"telegram": "@demo_teacher"},
                    "metadata": {"demo": True},
                },
            )
            self.created.teachers[entry["id"]] = teacher

        classroom_entries = [
            {
                "key": "room-pokrovka-101",
                "campus": "hse-pokrovka",
                "name": "Аудитория 101",
                "building": "Корпус А",
                "address": "Москва, Покровский бул., 11, стр. 4",
                "capacity": 80,
                "equipment": ["projector", "whiteboard"],
            },
            {
                "key": "room-itmo-510",
                "campus": "itmo-kronverksky",
                "name": "Лаборатория 510",
                "building": "Главный корпус",
                "address": "Санкт-Петербург, Кронверкский пр-т, 49",
                "capacity": 25,
                "equipment": ["vr-kit", "3d-printer"],
            },
            {
                "key": "room-msu-observatory",
                "campus": "msu-main",
                "name": "Обсерватория 201",
                "building": "Обсерваторский корпус",
                "address": "Москва, Ленинские горы, д. 1",
                "capacity": 20,
                "equipment": ["telescope", "spectrometer"],
            },
            {
                "key": "room-spbu-law-12",
                "campus": "spbu-vasileostrovsky",
                "name": "Аудитория 12",
                "building": "Юридический корпус",
                "address": "Санкт-Петербург, Университетская наб., 7/9",
                "capacity": 60,
                "equipment": ["projector", "video"],
            },
            {
                "key": "room-virtual-max",
                "campus": "hse-pokrovka",
                "name": "Онлайн-аудитория MAX",
                "building": "Виртуальный кампус",
                "address": "https://meet.example.com/max",
                "capacity": 300,
                "equipment": ["streaming"],
            },
        ]
        for entry in classroom_entries:
            campus = self.created.campuses[entry["campus"]]
            classroom, _ = models.Classroom.objects.update_or_create(
                name=entry["name"],
                campus=campus,
                defaults={
                    "building": entry["building"],
                    "address": entry["address"],
                    "capacity": entry["capacity"],
                    "equipment": entry["equipment"],
                    "metadata": {"demo": True},
                },
            )
            self.created.classrooms[entry["key"]] = classroom

        course_entries = [
            {
                "id": "course-algo",
                "title": "Алгоритмы и структуры данных",
                "kind": models.COURSE_KIND_CORE,
                "term": "2024-fall",
                "department": "hse-cs-dept",
                "format": models.COURSE_FORMAT_OFFLINE,
                "language": "ru",
                "ects": Decimal("6.0"),
                "workload_hours": 108,
                "digital_faculty": False,
                "description": "Классический курс по алгоритмам: сортировки, графы, динамическое программирование.",
                "teacher_ids": ["teacher-petrov"],
            },
            {
                "id": "course-ai-lab",
                "title": "Практикум по искусственному интеллекту",
                "kind": models.COURSE_KIND_ELECTIVE,
                "term": "2024-fall",
                "department": "itmo-ai-dept",
                "format": models.COURSE_FORMAT_HYBRID,
                "language": "ru",
                "ects": Decimal("4.0"),
                "workload_hours": 72,
                "digital_faculty": True,
                "description": "Практические кейсы по компьютерному зрению и робототехнике.",
                "teacher_ids": ["teacher-smirnova"],
            },
            {
                "id": "course-astro-data",
                "title": "Анализ космических данных",
                "kind": models.COURSE_KIND_CORE,
                "term": "2024-fall",
                "department": "msu-astro-dept",
                "format": models.COURSE_FORMAT_HYBRID,
                "language": "ru",
                "ects": Decimal("5.0"),
                "workload_hours": 90,
                "digital_faculty": False,
                "description": "Обработка телескопических данных, спектральный анализ и машинное обучение.",
                "teacher_ids": ["teacher-ivanova"],
            },
            {
                "id": "course-law-clinic",
                "title": "Правовая клиника: международные кейсы",
                "kind": models.COURSE_KIND_ELECTIVE,
                "term": "2024-fall",
                "department": "spbu-civil-dept",
                "format": models.COURSE_FORMAT_OFFLINE,
                "language": "ru",
                "ects": Decimal("3.0"),
                "workload_hours": 54,
                "digital_faculty": False,
                "description": "Практика подготовки документов и судебных выступлений для международных споров.",
                "teacher_ids": ["teacher-orlov"],
            },
            {
                "id": "course-digital-product",
                "title": "Управление цифровыми продуктами",
                "kind": models.COURSE_KIND_DIGITAL,
                "term": "2024-fall",
                "department": "hse-cs-dept",
                "format": models.COURSE_FORMAT_ONLINE,
                "language": "ru",
                "ects": Decimal("4.0"),
                "workload_hours": 64,
                "digital_faculty": True,
                "description": "Стратегия развития продуктов, метрики и A/B тесты.",
                "teacher_ids": ["teacher-petrov"],
            },
        ]

        for entry in course_entries:
            department = self.created.departments.get(entry["department"])
            course, _ = models.AcademicCourse.objects.update_or_create(
                id=entry["id"],
                defaults={
                    "kind": entry["kind"],
                    "title": entry["title"],
                    "short_title": entry["title"][:40],
                    "term": entry["term"],
                    "department": department,
                    "format": entry["format"],
                    "language": entry["language"],
                    "ects": entry["ects"],
                    "workload_hours": entry["workload_hours"],
                    "digital_faculty": entry["digital_faculty"],
                    "description": entry["description"],
                    "schedule_preview": [],
                    "quota": {"total": 120},
                    "enroll_window": {"from": "2024-08-01", "to": "2024-08-25"},
                    "prerequisites": ["Discrete Math"],
                    "anti_conflicts": {},
                    "rating": {"avg": 4.8},
                    "links": {"syllabus": "https://lms.example.com/course"},
                    "metadata": {"demo": True},
                },
            )
            teacher_objs = [self.created.teachers[tid] for tid in entry["teacher_ids"]]
            course.teachers.set(teacher_objs)
            self.created.courses[course.id] = course

        now = timezone.now()
        lesson_entries = [
            {
                "id": "lesson-algo-1",
                "course": "course-algo",
                "subject": "Алгоритмы: графы и обходы",
                "lesson_type": "lecture",
                "starts_at": now + timedelta(days=1, hours=9 - now.hour),
                "duration_hours": 2,
                "format": models.COURSE_FORMAT_OFFLINE,
                "room": "room-pokrovka-101",
                "teacher": "teacher-petrov",
                "group": "CS-101",
            },
            {
                "id": "lesson-algo-2",
                "course": "course-algo",
                "subject": "Семинар: динамическое программирование",
                "lesson_type": "seminar",
                "starts_at": now + timedelta(days=3, hours=11 - now.hour),
                "duration_hours": 2,
                "format": models.COURSE_FORMAT_OFFLINE,
                "room": "room-pokrovka-101",
                "teacher": "teacher-petrov",
                "group": "CS-101",
            },
            {
                "id": "lesson-ai-1",
                "course": "course-ai-lab",
                "subject": "Лаборатория: управление манипулятором",
                "lesson_type": "lab",
                "starts_at": now + timedelta(days=2, hours=10 - now.hour),
                "duration_hours": 3,
                "format": models.COURSE_FORMAT_HYBRID,
                "room": "room-itmo-510",
                "teacher": "teacher-smirnova",
                "group": "AI-202",
            },
            {
                "id": "lesson-astro-1",
                "course": "course-astro-data",
                "subject": "Обработка снимков телескопа",
                "lesson_type": "lecture",
                "starts_at": now + timedelta(days=4, hours=12 - now.hour),
                "duration_hours": 2,
                "format": models.COURSE_FORMAT_HYBRID,
                "room": "room-msu-observatory",
                "teacher": "teacher-ivanova",
                "group": "PHYS-401",
            },
            {
                "id": "lesson-law-1",
                "course": "course-law-clinic",
                "subject": "Разбор международного кейса",
                "lesson_type": "seminar",
                "starts_at": now + timedelta(days=6, hours=15 - now.hour),
                "duration_hours": 2,
                "format": models.COURSE_FORMAT_OFFLINE,
                "room": "room-spbu-law-12",
                "teacher": "teacher-orlov",
                "group": "LAW-101",
            },
            {
                "id": "lesson-digital-1",
                "course": "course-digital-product",
                "subject": "Метрики продуктового роста",
                "lesson_type": "lecture",
                "starts_at": now + timedelta(days=5, hours=18 - now.hour),
                "duration_hours": 1,
                "format": models.COURSE_FORMAT_ONLINE,
                "room": "room-virtual-max",
                "teacher": "teacher-petrov",
                "group": "DIGI-001",
            },
        ]

        for entry in lesson_entries:
            starts_at = entry["starts_at"]
            ends_at = starts_at + timedelta(hours=entry["duration_hours"])
            course = self.created.courses.get(entry["course"])
            teacher = self.created.teachers.get(entry["teacher"])
            group = self.created.groups.get(entry["group"])
            classroom = self.created.classrooms.get(entry["room"])
            models.Lesson.objects.update_or_create(
                id=entry["id"],
                defaults={
                    "course": course,
                    "subject": entry["subject"],
                    "lesson_type": entry["lesson_type"],
                    "starts_at": starts_at,
                    "ends_at": ends_at,
                    "format": entry["format"],
                    "room": classroom,
                    "room_snapshot": {"campus": classroom.campus.title if classroom else None},
                    "teacher": teacher,
                    "teacher_snapshot": {"full_name": teacher.full_name if teacher else ""},
                    "group": group,
                    "links": {"meet": "https://meet.example.com/demo"},
                    "notes": "Принести ноутбуки",
                    "status": models.LESSON_STATUS_SCHEDULED,
                    "series": {"weekday": starts_at.weekday()},
                },
            )

        student = self.created.users.get("student")
        course = self.created.courses.get("course-algo")
        teacher = self.created.teachers.get("teacher-petrov")
        if student and course and teacher:
            models.TeacherFeedback.objects.update_or_create(
                user=student,
                teacher=teacher,
                course=course,
                period=f"{now.year}",
                defaults={
                    "rating": 5,
                    "comment": "Интересные примеры и практические задания.",
                    "anonymous": False,
                    "tags": ["интерактивность", "структура курса"],
                    "status": models.TeacherFeedback.STATUS_ACCEPTED,
                    "visibility": {"public": True},
                },
            )

            models.ElectiveEnrollment.objects.update_or_create(
                user=student,
                course=self.created.courses["course-ai-lab"],
                term="2024-fall",
                defaults={
                    "status": models.ENROLLMENT_STATUS_PENDING,
                    "priority": 1,
                    "waitlist_position": 3,
                    "consents": {"personal_data": True},
                    "timestamps": {"created_at": now.isoformat()},
                },
            )

            models.ElectiveEnrollment.objects.update_or_create(
                user=student,
                course=self.created.courses["course-digital-product"],
                term="2024-fall",
                defaults={
                    "status": models.ENROLLMENT_STATUS_ENROLLED,
                    "priority": 1,
                    "waitlist_position": None,
                    "consents": {"personal_data": True},
                    "timestamps": {"created_at": now.isoformat()},
                },
            )

        applicant = self.created.users.get("applicant")
        if applicant:
            models.TeacherFeedback.objects.update_or_create(
                user=applicant,
                teacher=self.created.teachers["teacher-smirnova"],
                course=self.created.courses["course-ai-lab"],
                period=f"{now.year}",
                defaults={
                    "rating": 4,
                    "comment": "Хотелось бы больше практики по робототехнике.",
                    "anonymous": True,
                    "tags": ["практика"],
                    "status": models.TeacherFeedback.STATUS_PENDING,
                    "visibility": {"public": False},
                },
            )

            models.ElectiveEnrollment.objects.update_or_create(
                user=applicant,
                course=self.created.courses["course-law-clinic"],
                term="2024-fall",
                defaults={
                    "status": models.ENROLLMENT_STATUS_WAITLISTED,
                    "priority": 2,
                    "waitlist_position": 5,
                    "consents": {"personal_data": True},
                    "timestamps": {"created_at": now.isoformat()},
                },
            )

        self.log("✓ Преподаватели, курсы, занятия и заявки на электив подготовлены")

    # ------------------------------------------------------------------ users

    def seed_users(self) -> None:
        user_entries = [
            {
                "key": "student",
                "user_id": "ext-100500",
                "role": models.UserProfile.ROLE_STUDENT,
                "scopes": ["schedule:read", "projects:write", "dorm:manage", "library:read"],
                "full_name": "Максим Иванов",
                "email": "max@example.com",
                "locale": "ru",
                "time_zone": "Europe/Moscow",
                "academic_group": "CS-101",
            },
            {
                "key": "staff",
                "user_id": "ext-200600",
                "role": models.UserProfile.ROLE_STAFF,
                "scopes": ["projects:moderate", "dashboards:read"],
                "full_name": "Елена Кузнецова",
                "email": "elena.kuznetsova@example.com",
                "locale": "ru",
                "time_zone": "Europe/Moscow",
                "academic_group": None,
            },
            {
                "key": "deanery",
                "user_id": "ext-300700",
                "role": models.UserProfile.ROLE_DEANERY,
                "scopes": ["deanery:manage"],
                "full_name": "Олег Миронов",
                "email": "deanery@example.com",
                "locale": "ru",
                "time_zone": "Europe/Moscow",
                "academic_group": None,
            },
            {
                "key": "applicant",
                "user_id": "ext-400800",
                "role": models.UserProfile.ROLE_APPLICANT,
                "scopes": ["admissions:read"],
                "full_name": "Анна Заявкина",
                "email": "anna.applicant@example.com",
                "locale": "ru",
                "time_zone": "Europe/Moscow",
                "academic_group": None,
            },
            {
                "key": "career_center",
                "user_id": "ext-500900",
                "role": models.UserProfile.ROLE_CAREER_CENTER,
                "scopes": ["career:manage"],
                "full_name": "Роман Сергеев",
                "email": "career@example.com",
                "locale": "ru",
                "time_zone": "Europe/Moscow",
                "academic_group": None,
            },
            {
                "key": "librarian",
                "user_id": "ext-600010",
                "role": models.UserProfile.ROLE_LIBRARIAN,
                "scopes": ["library:manage"],
                "full_name": "Марина Лебедева",
                "email": "library@example.com",
                "locale": "ru",
                "time_zone": "Europe/Moscow",
                "academic_group": None,
            },
        ]

        for entry in user_entries:
            academic_group = self.created.groups.get(entry["academic_group"])
            profile, _ = models.UserProfile.objects.update_or_create(
                user_id=entry["user_id"],
                defaults={
                    "role": entry["role"],
                    "scopes": entry["scopes"],
                    "full_name": entry["full_name"],
                    "email": entry["email"],
                    "locale": entry["locale"],
                    "time_zone": entry["time_zone"],
                    "academic_group": academic_group,
                    "metadata": {"demo": True},
                },
            )
            self.created.users[entry["key"]] = profile

        self.log("✓ Профили пользователей созданы")

    # ------------------------------------------------------------------ projects

    def seed_projects(self) -> None:
        owner = self.created.users["student"]
        department = self.created.departments["hse-cs-dept"]
        project, _ = models.Project.objects.update_or_create(
            code="PRJ-0001",
            defaults={
                "owner_type": models.PROJECT_OWNER_STUDENT,
                "owner_user": owner,
                "department": department,
                "title": "Платформа рекомендаций для обучения",
                "summary": "Сервис подбора образовательных треков для студентов MAX Campus.",
                "description_md": (
                    "## Цель\n"
                    "Создать интеллектуальную платформу, которая анализирует траекторию студента и советует подходящие курсы.\n\n"
                    "### Задачи\n"
                    "- Интеграция с расписанием и системой заявок\n"
                    "- Разработка рекомендательной модели\n"
                    "- Дизайн интерфейса мини-приложения"
                ),
                "domain_tags": ["edtech", "ai"],
                "skills_required": ["python", "ml", "vue"],
                "format": models.PROJECT_FORMAT_INTRA,
                "links": {"figma": "https://figma.example.com/project"},
                "timeline": {"start": "2024-09", "finish": "2025-02"},
                "team": {"desired_size": 6, "roles": ["backend", "frontend", "data"]},
                "constraints": {"workload_hours_per_week": 12},
                "education": {"ects": 6, "track": "Проектный модуль"},
                "contacts": {"email": owner.email},
                "moderation": {"required": False},
                "metrics": {"applications": 4},
                "media": {"cover_url": "https://cdn.example.com/demo/project-cover.jpg"},
                "status": models.PROJECT_STATUS_APPROVED,
                "published_at": timezone.now() - timedelta(days=5),
                "extra": {"demo": True},
            },
        )
        self.created.projects["recommendation-platform"] = project

        vacancy, _ = models.ProjectVacancy.objects.update_or_create(
            project=project,
            role_code="backend",
            defaults={
                "title": "Backend-разработчик",
                "description": "Разработка API и интеграция с сервисами кампуса.",
                "skills": ["python", "fastapi", "postgresql"],
                "count_total": 2,
                "count_open": 1,
                "experience_level": "middle",
                "metadata": {"demo": True},
            },
        )

        applicant = self.created.users["student"]
        models.ProjectApplication.objects.update_or_create(
            project=project,
            user=applicant,
            defaults={
                "vacancy": vacancy,
                "motivation": "Хочу развивать рекомендательные системы и уже работал с FastAPI.",
                "attachments": [{"name": "cv.pdf", "url": "https://files.example.com/cv.pdf"}],
                "status": models.APPLICATION_STATUS_ACCEPTED,
                "cv_url": "https://files.example.com/cv.pdf",
                "portfolio_url": "https://github.com/max-student",
                "consents": {"personal_data": True},
                "feedback": {"mentor": "Готов подключить наставника из индустрии"},
                "metadata": {"demo": True},
            },
        )

        models.ProjectTeamMembership.objects.update_or_create(
            project=project,
            user=owner,
            role=models.ProjectTeamMembership.ROLE_OWNER,
            role_code="owner",
            defaults={
                "responsibility": "Общее управление, координация команды и разработка backend.",
                "joined_at": date.today() - timedelta(days=30),
                "allocation": {"hours_per_week": 15},
                "contacts": {"telegram": "@max_owner"},
            },
        )

        models.ProjectTask.objects.update_or_create(
            project=project,
            external_id="JIRA-101",
            defaults={
                "title": "Настроить CI/CD пайплайн",
                "description": "Сборка контейнера, настройка линтеров и автоматических тестов.",
                "status": models.TASK_STATUS_IN_PROGRESS,
                "assignees": [owner.full_name],
                "labels": ["devops"],
                "due_date": date.today() + timedelta(days=14),
                "tracker_payload": {"url": "https://tracker.example.com/JIRA-101"},
            },
        )

        models.ProjectSubscription.objects.update_or_create(
            project=project,
            user=self.created.users["staff"],
            defaults={
                "channels": ["in_app", "email"],
                "metadata": {"demo": True},
            },
        )

        dept_owner = self.created.departments["msu-astro-dept"]
        astro_project, _ = models.Project.objects.update_or_create(
            code="PRJ-0002",
            defaults={
                "owner_type": models.PROJECT_OWNER_DEPARTMENT,
                "owner_user": self.created.users["staff"],
                "department": dept_owner,
                "title": "Система мониторинга космических событий",
                "summary": "Платформа для агрегации и визуализации данных астрономических наблюдений.",
                "description_md": (
                    "## Цели проекта\n"
                    "- Автоматизировать сбор телескопических данных\n"
                    "- Выявлять интересные события (сверхновые, вспышки)\n"
                    "- Отправлять уведомления исследователям\n"
                ),
                "domain_tags": ["astro", "data-platform"],
                "skills_required": ["python", "django", "bigquery"],
                "format": models.PROJECT_FORMAT_RESEARCH,
                "links": {"spec": "https://docs.example.com/astro-monitoring"},
                "timeline": {"start": "2024-05", "finish": "2025-01"},
                "team": {"desired_size": 4, "roles": ["backend", "data"]},
                "constraints": {"workload_hours_per_week": 10},
                "education": {"ects": 4, "track": "Научно-исследовательский модуль"},
                "contacts": {"email": "astro-lab@example.com"},
                "moderation": {"required": True},
                "metrics": {"applications": 2},
                "media": {"cover_url": "https://cdn.example.com/demo/astro-project.jpg"},
                "status": models.PROJECT_STATUS_PENDING,
                "published_at": timezone.now() - timedelta(days=2),
                "extra": {"demo": True},
            },
        )
        self.created.projects["astro-monitoring"] = astro_project

        models.ProjectVacancy.objects.update_or_create(
            project=astro_project,
            role_code="data_scientist",
            defaults={
                "title": "Data Scientist",
                "description": "Разработка моделей выявления аномалий и построения алертов.",
                "skills": ["python", "pandas", "airflow"],
                "count_total": 1,
                "count_open": 1,
                "experience_level": "junior",
                "metadata": {"demo": True},
            },
        )

        applicant = self.created.users.get("applicant")
        if applicant:
            models.ProjectApplication.objects.update_or_create(
                project=astro_project,
                user=applicant,
                defaults={
                    "vacancy": None,
                    "motivation": "Изучаю анализ данных и хочу применить знания к космическим данным.",
                    "attachments": [{"name": "pet-project.pdf", "url": "https://files.example.com/pet.pdf"}],
                    "status": models.APPLICATION_STATUS_NEW,
                    "cv_url": "https://files.example.com/cv-applicant.pdf",
                    "portfolio_url": "https://behance.example.com/applicant",
                    "consents": {"personal_data": True},
                    "metadata": {"demo": True},
                },
            )

        models.ProjectTeamMembership.objects.update_or_create(
            project=astro_project,
            user=self.created.users["staff"],
            role=models.ProjectTeamMembership.ROLE_CURATOR,
            role_code="curator",
            defaults={
                "responsibility": "Наставничество и контроль сроков выполнения.",
                "joined_at": date.today() - timedelta(days=15),
                "allocation": {"hours_per_week": 6},
                "contacts": {"email": "elena.kuznetsova@example.com"},
            },
        )

        models.ProjectTask.objects.update_or_create(
            project=astro_project,
            external_id="ASTRO-5",
            defaults={
                "title": "Подготовить датасет телескопов",
                "description": "Собрать исторические данные наблюдений и загрузить в data lake.",
                "status": models.TASK_STATUS_DONE,
                "assignees": ["Мария Иванова"],
                "labels": ["data", "ingestion"],
                "due_date": date.today() - timedelta(days=1),
                "tracker_payload": {"url": "https://tracker.example.com/ASTRO-5"},
            },
        )

        models.ProjectSubscription.objects.update_or_create(
            project=astro_project,
            user=self.created.users["career_center"],
            defaults={
                "channels": ["email"],
                "metadata": {"demo": True, "context": "project_updates"},
            },
        )

        self.log("✓ Проекты и связанные сущности созданы")

    # -------------------------------------------------------------------- careers

    def seed_career_data(self) -> None:
        companies_data = [
            {
                "id": "comp-quantum-soft",
                "defaults": {
                    "name": "Quantum Soft",
                    "verified_partner": True,
                    "logo_url": "https://cdn.example.com/demo/quantum-logo.png",
                    "site_url": "https://quantumsoft.example.com",
                    "description": "Компания-разработчик решений в области анализа данных и автоматизации.",
                    "contacts": {"email": "hr@quantumsoft.example.com"},
                    "metadata": {"demo": True},
                },
            },
            {
                "id": "comp-green-tech",
                "defaults": {
                    "name": "GreenTech Labs",
                    "verified_partner": False,
                    "logo_url": "https://cdn.example.com/demo/greentech-logo.png",
                    "site_url": "https://greentech.example.com",
                    "description": "Стартап, создающий IoT-системы для устойчивых городов.",
                    "contacts": {"email": "jobs@greentech.example.com"},
                    "metadata": {"demo": True},
                },
            },
            {
                "id": "comp-north-bank",
                "defaults": {
                    "name": "North Bank",
                    "verified_partner": True,
                    "logo_url": "https://cdn.example.com/demo/northbank-logo.png",
                    "site_url": "https://northbank.example.com",
                    "description": "Финансовая группа, развивающая цифровые продукты для клиентов.",
                    "contacts": {"email": "talent@northbank.example.com"},
                    "metadata": {"demo": True},
                },
            },
        ]

        companies = {}
        for entry in companies_data:
            company, _ = models.CareerCompany.objects.update_or_create(
                id=entry["id"],
                defaults=entry["defaults"],
            )
            companies[entry["id"]] = company

        vacancy_entries = [
            {
                "id": "vacancy-data-analyst",
                "company": "comp-quantum-soft",
                "title": "Младший аналитик данных",
                "direction": ["analytics", "product"],
                "grade": "junior",
                "employment": "full_time",
                "location": {"type": "hybrid", "city": "Москва", "country": "Россия"},
                "visa_sponsorship": False,
                "relocation": True,
                "salary": {"from": 90000, "to": 120000, "currency": "RUB", "gross": True},
                "requirements": {"education": "Высшее техническое", "stack": ["SQL", "Python", "Tableau"]},
                "responsibilities": [
                    "Подготовка отчётов и дашбордов",
                    "Построение продуктовых метрик",
                ],
                "benefits": ["ДМС", "Корпоративное обучение"],
                "skills": ["python", "sql", "tableau"],
                "experience_min_years": 1,
                "language_requirements": {"english": "B2"},
                "apply": {"email": "jobs@quantumsoft.example.com"},
                "source": {"type": "internal"},
                "posted_days_ago": 3,
                "duration_days": 30,
            },
            {
                "id": "vacancy-backend-go",
                "company": "comp-green-tech",
                "title": "Backend-разработчик (Go)",
                "direction": ["engineering"],
                "grade": "middle",
                "employment": "full_time",
                "location": {"type": "remote", "country": "Россия"},
                "visa_sponsorship": False,
                "relocation": False,
                "salary": {"from": 180000, "to": 240000, "currency": "RUB", "gross": True},
                "requirements": {
                    "stack": ["Go", "PostgreSQL", "Kafka"],
                    "experience": "от 2 лет коммерческой разработки",
                },
                "responsibilities": [
                    "Разработка микросервисов для IoT-платформы",
                    "Настройка потоков данных и интеграция с аналитикой",
                ],
                "benefits": ["Удалённая работа", "Оплата конференций"],
                "skills": ["go", "kubernetes", "event-driven"],
                "experience_min_years": 2,
                "language_requirements": {"english": "B1"},
                "apply": {"url": "https://greentech.example.com/jobs/backend"},
                "source": {"type": "external", "provider": "hh.ru"},
                "posted_days_ago": 7,
                "duration_days": 45,
            },
            {
                "id": "vacancy-ui-designer",
                "company": "comp-north-bank",
                "title": "UI/UX дизайнер цифровых сервисов",
                "direction": ["design", "product"],
                "grade": "middle",
                "employment": "part_time",
                "location": {"type": "on_site", "city": "Санкт-Петербург", "country": "Россия"},
                "visa_sponsorship": False,
                "relocation": True,
                "salary": {"from": 140000, "to": 170000, "currency": "RUB", "gross": True},
                "requirements": {"portfolio": True, "tools": ["Figma", "Miro", "Adobe CC"]},
                "responsibilities": [
                    "Проектирование интерфейсов мобильного банка",
                    "Проведение пользовательских интервью",
                ],
                "benefits": ["Гибкий график", "Льготная ипотека"],
                "skills": ["figma", "ux_research"],
                "experience_min_years": 3,
                "language_requirements": {"english": "A2"},
                "apply": {"email": "talent@northbank.example.com"},
                "source": {"type": "referral"},
                "posted_days_ago": 1,
                "duration_days": 25,
            },
        ]

        for entry in vacancy_entries:
            posted_at = timezone.now() - timedelta(days=entry["posted_days_ago"])
            vacancy, _ = models.CareerVacancy.objects.update_or_create(
                id=entry["id"],
                defaults={
                    "title": entry["title"],
                    "company": companies[entry["company"]],
                    "direction": entry["direction"],
                    "grade": entry["grade"],
                    "employment": entry["employment"],
                    "location": entry["location"],
                    "visa_sponsorship": entry["visa_sponsorship"],
                    "relocation": entry["relocation"],
                    "salary": entry["salary"],
                    "requirements": entry["requirements"],
                    "responsibilities": entry["responsibilities"],
                    "benefits": entry["benefits"],
                    "skills": entry["skills"],
                    "experience_min_years": entry["experience_min_years"],
                    "language_requirements": entry["language_requirements"],
                    "apply_window": {"from": posted_at.date().isoformat()},
                    "apply": entry["apply"],
                    "source": entry["source"],
                    "status": entry.get("status", models.VACANCY_STATUS_PUBLISHED),
                    "posted_at": posted_at,
                    "published_until": posted_at + timedelta(days=entry["duration_days"]),
                    "metadata": {"demo": True},
                },
            )
            self.created.career_vacancies[vacancy.id] = vacancy

        application_entries = [
            {
                "vacancy": "vacancy-data-analyst",
                "user": "student",
                "defaults": {
                    "resume_url": "https://files.example.com/resume.pdf",
                    "cover_letter": "Готов применить навыки анализа данных и машинного обучения на реальных задачах.",
                    "portfolio_links": ["https://github.com/max-student/data-projects"],
                    "answers": {"relocation": "готов", "experience": "участие в университетских проектах"},
                    "consents": {"personal_data": True},
                    "status": models.CAREER_APPLICATION_STATUS_IN_REVIEW,
                    "status_history": [
                        {"status": "submitted", "at": (timezone.now() - timedelta(days=2)).isoformat()},
                        {"status": "in_review", "at": (timezone.now() - timedelta(days=1)).isoformat()},
                    ],
                    "interviews": [
                        {
                            "type": "technical",
                            "scheduled_at": (timezone.now() + timedelta(days=2)).isoformat(),
                        }
                    ],
                    "notifications": {"email": True},
                },
            },
            {
                "vacancy": "vacancy-backend-go",
                "user": "student",
                "defaults": {
                    "resume_url": "https://files.example.com/resume-backend.pdf",
                    "cover_letter": "Опыт разработки микросервисов и построения CI/CD.",
                    "portfolio_links": ["https://github.com/max-student/go-iot"],
                    "answers": {"remote": "да", "expected_salary": "220000"},
                    "consents": {"personal_data": True},
                    "status": models.CAREER_APPLICATION_STATUS_INVITED,
                    "status_history": [
                        {"status": "submitted", "at": (timezone.now() - timedelta(days=5)).isoformat()},
                        {"status": "in_review", "at": (timezone.now() - timedelta(days=3)).isoformat()},
                        {"status": "invited", "at": timezone.now().isoformat()},
                    ],
                    "interviews": [
                        {"type": "culture", "scheduled_at": (timezone.now() + timedelta(days=4)).isoformat()}
                    ],
                    "notifications": {"email": True, "sms": True},
                },
            },
            {
                "vacancy": "vacancy-ui-designer",
                "user": "applicant",
                "defaults": {
                    "resume_url": "https://files.example.com/resume-ux.pdf",
                    "cover_letter": "Хочу развивать интерфейсы банков и умею работать с Figma.",
                    "portfolio_links": ["https://dribbble.com/applicant"],
                    "answers": {"relocation": "возможен", "experience": "3 года в финтехе"},
                    "consents": {"personal_data": True},
                    "status": models.CAREER_APPLICATION_STATUS_SUBMITTED,
                    "status_history": [
                        {"status": "submitted", "at": timezone.now().isoformat()},
                    ],
                    "interviews": [],
                    "notifications": {"email": True},
                },
            },
        ]

        for entry in application_entries:
            user = self.created.users.get(entry["user"])
            vacancy = self.created.career_vacancies.get(entry["vacancy"])
            if not user or not vacancy:
                continue
            models.CareerVacancyApplication.objects.update_or_create(
                vacancy=vacancy,
                user=user,
                defaults={**entry["defaults"], "metadata": {"demo": True}},
            )

        counselor = self.created.users.get("career_center") or self.created.users["staff"]
        consultations = [
            {
                "user": "student",
                "topic": "Подготовка к собеседованию",
                "defaults": {
                    "subtopic": "Data Analyst",
                    "preferred_slots": [
                        {"date": (date.today() + timedelta(days=3)).isoformat(), "time": "10:00-11:00"},
                        {"date": (date.today() + timedelta(days=4)).isoformat(), "time": "15:00-16:00"},
                    ],
                    "preferred_channel": "video_call",
                    "counselor": counselor,
                    "scheduled_at": timezone.now() + timedelta(days=3, hours=10),
                    "duration_minutes": 60,
                    "channel_details": {"link": "https://meet.example.com/career"},
                    "status": models.CONSULTATION_STATUS_SCHEDULED,
                    "notes": {"agenda": "Разбор резюме и портфолио"},
                },
            },
            {
                "user": "applicant",
                "topic": "Карьерная траектория",
                "defaults": {
                    "subtopic": "Дизайн цифровых продуктов",
                    "preferred_slots": [
                        {"date": (date.today() + timedelta(days=6)).isoformat(), "time": "12:00-13:00"},
                    ],
                    "preferred_channel": "in_person",
                    "counselor": counselor,
                    "scheduled_at": timezone.now() - timedelta(days=1),
                    "duration_minutes": 45,
                    "channel_details": {"office": "Москва, Покровский бул., 11"},
                    "status": models.CONSULTATION_STATUS_COMPLETED,
                    "notes": {"summary": "Определили план развития портфолио"},
                },
            },
        ]

        for entry in consultations:
            user = self.created.users.get(entry["user"])
            if not user:
                continue
            models.CareerConsultation.objects.update_or_create(
                user=user,
                topic=entry["topic"],
                defaults={**entry["defaults"], "metadata": {"demo": True}},
            )

        self.log("✓ Карьерный раздел заполнен")

    # -------------------------------------------------------------------- deanery

    def seed_deanery_data(self) -> None:
        student = self.created.users["student"]
        deanery_staff = self.created.users["deanery"]

        certificate, _ = models.DeaneryCertificateRequest.objects.update_or_create(
            user=student,
            certificate_type="Справка об обучении",
            defaults={
                "language": "ru",
                "purpose": "Предоставить работодателю",
                "copies_count": 1,
                "delivery_method": "pickup",
                "pickup_location": "Окно №3, корпус А",
                "digital_copy": True,
                "status": models.CERTIFICATE_STATUS_IN_PROGRESS,
                "sla": {"expected_days": 5},
                "processing": {"assigned_to": deanery_staff.full_name},
                "attachments": [{"name": "power_of_attorney.pdf", "url": "https://files.example.com/power.pdf"}],
                "metadata": {"demo": True},
            },
        )

        models.DeaneryCertificateRequest.objects.update_or_create(
            user=student,
            certificate_type="Справка о доходах",
            defaults={
                "language": "ru",
                "purpose": "Для налоговой инспекции",
                "copies_count": 2,
                "delivery_method": "digital",
                "pickup_location": "",
                "digital_copy": True,
                "status": models.CERTIFICATE_STATUS_READY,
                "sla": {"expected_days": 7},
                "processing": {"assigned_to": deanery_staff.full_name, "completed_at": timezone.now().isoformat()},
                "metadata": {"demo": True},
            },
        )

        invoice, _ = models.TuitionInvoice.objects.update_or_create(
            user=student,
            term="2024-fall",
            defaults={
                "amount": Decimal("120000.00"),
                "currency": "RUB",
                "due_date": date.today().replace(month=9, day=1),
                "description": "Оплата за осенний семестр 2024",
                "status": "pending",
                "payment_method": "",
                "metadata": {"demo": True},
            },
        )

        invoice_spring, _ = models.TuitionInvoice.objects.update_or_create(
            user=student,
            term="2024-spring",
            defaults={
                "amount": Decimal("115000.00"),
                "currency": "RUB",
                "due_date": date.today().replace(month=2, day=1),
                "description": "Оплата за весенний семестр 2024",
                "status": "paid",
                "paid_at": timezone.now() - timedelta(days=90),
                "payment_method": "card",
                "metadata": {"demo": True},
            },
        )

        models.TuitionPaymentIntent.objects.update_or_create(
            invoice=invoice,
            user=student,
            purpose="tuition_fall_2024",
            defaults={
                "amount": invoice.amount,
                "currency": invoice.currency,
                "status": models.PAYMENT_INTENT_STATUS_PROCESSING,
                "confirmation_url": "https://payments.example.com/confirm/tuition",
                "provider_payload": {"provider": "demo-pay"},
                "metadata": {"demo": True},
            },
        )

        models.TuitionPaymentIntent.objects.update_or_create(
            invoice=invoice_spring,
            user=student,
            purpose="tuition_spring_2024",
            defaults={
                "amount": invoice_spring.amount,
                "currency": invoice_spring.currency,
                "status": models.PAYMENT_INTENT_STATUS_SUCCEEDED,
                "confirmation_url": "https://payments.example.com/confirm/tuition-spring",
                "provider_payload": {"provider": "demo-pay", "receipt_id": "SPRING-2024"},
                "metadata": {"demo": True},
            },
        )

        models.DeaneryCompensationRequest.objects.update_or_create(
            user=student,
            compensation_type="Проезд на конференцию",
            defaults={
                "amount": Decimal("8500.00"),
                "currency": "RUB",
                "reason": "Компенсация расходов на командировку для выступления на митапе.",
                "bank_details": {"account": "40817810000001000001", "bank": "Demo Bank"},
                "documents": [{"name": "receipt.pdf", "url": "https://files.example.com/receipt.pdf"}],
                "status": models.COMPENSATION_STATUS_IN_REVIEW,
                "metadata": {"demo": True},
            },
        )

        models.DeaneryCompensationRequest.objects.update_or_create(
            user=student,
            compensation_type="Оплата участия в олимпиаде",
            defaults={
                "amount": Decimal("3500.00"),
                "currency": "RUB",
                "reason": "Возмещение организационного взноса за олимпиаду по программированию.",
                "bank_details": {"account": "40817810000001000002", "bank": "Demo Bank"},
                "documents": [{"name": "fee_receipt.pdf", "url": "https://files.example.com/fee.pdf"}],
                "status": models.COMPENSATION_STATUS_APPROVED,
                "metadata": {"demo": True},
            },
        )

        models.DeaneryTransferRequest.objects.update_or_create(
            user=student,
            defaults={
                "from_program": self.created.programs["prog-hse-se"],
                "to_program": self.created.programs["prog-hse-data"],
                "desired_term": "spring-2025",
                "reason": "Хочу углубиться в анализ данных и пройти проектный модуль в Data Science.",
                "documents": [],
                "status": models.TRANSFER_STATUS_IN_REVIEW,
                "workflow": {"assigned_to": deanery_staff.full_name},
                "metadata": {"demo": True},
            },
        )

        models.AcademicLeaveRequest.objects.update_or_create(
            user=student,
            reason="Стажировка за рубежом",
            defaults={
                "leave_from": date.today().replace(year=date.today().year - 1, month=1, day=15),
                "leave_to": date.today().replace(year=date.today().year - 1, month=6, day=30),
                "documents": [{"name": "internship_agreement.pdf", "url": "https://files.example.com/internship.pdf"}],
                "advisor": "Анна Смирнова",
                "status": models.ACADEMIC_LEAVE_STATUS_COMPLETED,
                "metadata": {"demo": True},
            },
        )

        models.AcademicLeaveRequest.objects.update_or_create(
            user=student,
            reason="Необходимость длительного медицинского лечения",
            defaults={
                "leave_from": date.today().replace(month=10, day=1),
                "leave_to": date.today().replace(year=date.today().year + 1, month=2, day=1),
                "documents": [{"name": "medical_certificate.pdf", "url": "https://files.example.com/med.pdf"}],
                "advisor": "Иван Петров",
                "status": models.ACADEMIC_LEAVE_STATUS_IN_REVIEW,
                "metadata": {"demo": True},
            },
        )

        self.log("✓ Деканат и финансовые данные загружены")

    # ----------------------------------------------------------------------- dorm

    def seed_dorm_data(self) -> None:
        student = self.created.users["student"]
        service_entries = [
            {
                "id": "dorm-cleaning",
                "title": "Уборка комнаты",
                "category": "maintenance",
                "description": "Плановая уборка комнаты в общежитии, включающая влажную уборку и вынос мусора.",
                "price_amount": Decimal("800.00"),
                "delivery_time": "В течение 24 часов",
                "availability": "available",
                "options": {"time_slots": ["09:00-12:00", "18:00-21:00"]},
                "required_fields": ["room", "preferred_time"],
            },
            {
                "id": "dorm-laundry",
                "title": "Прачечная",
                "category": "daily_life",
                "description": "Стирка и сушилка, включая средство для стирки.",
                "price_amount": Decimal("300.00"),
                "delivery_time": "В течение дня",
                "availability": "available",
                "options": {"machines": 4},
                "required_fields": ["room"],
            },
            {
                "id": "dorm-storage",
                "title": "Хранение вещей",
                "category": "storage",
                "description": "Камера хранения для чемоданов и сезонных вещей.",
                "price_amount": Decimal("500.00"),
                "delivery_time": "До 7 дней",
                "availability": "limited",
                "options": {"max_weight": "20kg"},
                "required_fields": ["room", "items"],
            },
        ]

        for entry in service_entries:
            service, _ = models.DormService.objects.update_or_create(
                id=entry["id"],
                defaults={
                    "title": entry["title"],
                    "category": entry["category"],
                    "description": entry["description"],
                    "price_amount": entry["price_amount"],
                    "price_currency": "RUB",
                    "delivery_time": entry["delivery_time"],
                    "availability": entry["availability"],
                    "options": entry["options"],
                    "required_fields": entry["required_fields"],
                    "metadata": {"demo": True},
                },
            )
            self.created.dorm_services[service.id] = service

        models.DormPaymentIntent.objects.update_or_create(
            user=student,
            period="2024-09",
            defaults={
                "residence": "Общежитие MAX Campus, корпус 3",
                "amount": Decimal("15000.00"),
                "currency": "RUB",
                "status": models.PAYMENT_INTENT_STATUS_SUCCEEDED,
                "confirmation_url": "https://payments.example.com/confirm/dorm",
                "purpose": "dorm_fee",
                "metadata": {"demo": True},
            },
        )

        models.DormPaymentIntent.objects.update_or_create(
            user=student,
            period="2024-10",
            defaults={
                "residence": "Общежитие MAX Campus, корпус 3",
                "amount": Decimal("15000.00"),
                "currency": "RUB",
                "status": models.PAYMENT_INTENT_STATUS_REQUIRES_ACTION,
                "confirmation_url": "https://payments.example.com/confirm/dorm-oct",
                "purpose": "dorm_fee",
                "metadata": {"demo": True},
            },
        )

        service = self.created.dorm_services["dorm-cleaning"]
        models.DormServiceOrder.objects.update_or_create(
            service=service,
            user=student,
            defaults={
                "payload": {"room": "A-101", "preferred_time": "09:00-12:00"},
                "status": "scheduled",
                "scheduled_for": timezone.now() + timedelta(days=1),
                "notifications": {"push": True},
                "metadata": {"demo": True},
            },
        )

        storage_service = self.created.dorm_services["dorm-storage"]
        models.DormServiceOrder.objects.update_or_create(
            service=storage_service,
            user=student,
            defaults={
                "payload": {"room": "A-101", "items": ["зимняя одежда"], "duration": "3 месяца"},
                "status": models.DORM_ORDER_STATUS_COMPLETED,
                "scheduled_for": timezone.now() - timedelta(days=40),
                "completed_at": timezone.now() - timedelta(days=30),
                "notifications": {"email": True},
                "metadata": {"demo": True},
            },
        )

        models.DormGuestPass.objects.update_or_create(
            user=student,
            guest_full_name="Пётр Сидоров",
            visit_date=date.today() + timedelta(days=2),
            defaults={
                "guest_document": {"type": "passport", "number": "4500 123456"},
                "visit_time_from": "10:00",
                "visit_time_to": "18:00",
                "notes": "Коллега по проекту",
                "status": "approved",
                "qr_code": {"payload": "DEMO-QR-CODE"},
                "metadata": {"demo": True},
            },
        )

        models.DormGuestPass.objects.update_or_create(
            user=student,
            guest_full_name="Екатерина Смирнова",
            visit_date=date.today() - timedelta(days=7),
            defaults={
                "guest_document": {"type": "passport", "number": "4000 765432"},
                "visit_time_from": "09:00",
                "visit_time_to": "12:00",
                "notes": "Семейный визит",
                "status": "used",
                "qr_code": {"payload": "USED-QR-001"},
                "metadata": {"demo": True},
            },
        )

        models.DormSupportTicket.objects.update_or_create(
            user=student,
            subject="Сломан кондиционер",
            defaults={
                "category": "maintenance",
                "description": "В комнате A-101 перестал работать кондиционер. Необходим ремонт.",
                "attachments": [{"name": "photo.jpg", "url": "https://files.example.com/cond.jpg"}],
                "status": "in_progress",
                "assigned_to": "Дежурный техник",
                "interactions": [{"at": timezone.now().isoformat(), "message": "Заявка принята"}],
                "metadata": {"demo": True},
            },
        )

        models.DormSupportTicket.objects.update_or_create(
            user=student,
            subject="Проблемы с интернетом",
            defaults={
                "category": "network",
                "description": "В общежитии наблюдаются перебои с Wi-Fi в вечернее время.",
                "attachments": [],
                "status": models.DORM_TICKET_STATUS_RESOLVED,
                "assigned_to": "Служба ИТ",
                "resolution": {"date": timezone.now().isoformat(), "details": "Перезапущены точки доступа"},
                "metadata": {"demo": True},
            },
        )

        self.log("✓ Общежитие: услуги, заказы и обращения созданы")

    # ----------------------------------------------------------------------- events

    def seed_events(self) -> None:
        events = [
            {
                "id": "event-max-hackathon",
                "title": "MAX Campus Hackathon",
                "subtitle": "Соревнование по разработке студенческих сервисов",
                "description": "48-часовой хакатон с участием студенческих команд и наставников из индустрии.",
                "category": "career",
                "starts_at": timezone.now() + timedelta(days=7),
                "ends_at": timezone.now() + timedelta(days=7, hours=36),
                "location": "Москва, Покровский бул., 11",
                "organizer": "MAX Campus",
                "cover": "https://cdn.example.com/demo/hackathon-cover.jpg",
                "capacity": 120,
                "remaining": 42,
                "registration_required": True,
                "registration_deadline": timezone.now() + timedelta(days=5),
                "tags": ["hackathon", "innovation"],
                "agenda": [
                    {"time": "10:00", "title": "Открытие"},
                    {"time": "18:00", "title": "Промежуточная презентация"},
                ],
                "links": {"landing": "https://events.example.com/hackathon"},
                "status": models.EVENT_STATUS_SCHEDULED,
                "visibility": "public",
            },
            {
                "id": "event-product-meetup",
                "title": "Product Meetup & Networking",
                "subtitle": "Встреча с выпускниками и менеджерами продуктов",
                "description": "Обсуждаем продуктовую аналитику и карьерный путь в IT-компаниях.",
                "category": "community",
                "starts_at": timezone.now() + timedelta(days=2),
                "ends_at": timezone.now() + timedelta(days=2, hours=3),
                "location": "Санкт-Петербург, Университетская наб., 7/9",
                "organizer": "MAX Alumni Club",
                "cover": "https://cdn.example.com/demo/product-meetup.jpg",
                "capacity": 80,
                "remaining": 10,
                "registration_required": True,
                "registration_deadline": timezone.now() + timedelta(days=1),
                "tags": ["product", "networking"],
                "agenda": [
                    {"time": "19:00", "title": "Приветствие"},
                    {"time": "19:30", "title": "Панельная дискуссия"},
                ],
                "links": {"landing": "https://events.example.com/product-meetup"},
                "status": models.EVENT_STATUS_SCHEDULED,
                "visibility": "students_only",
            },
            {
                "id": "event-remote-webinar",
                "title": "Webinar: Academic Writing Essentials",
                "subtitle": "",
                "description": "Онлайн-вебинар о том, как готовить академические статьи и отчёты.",
                "category": "education",
                "starts_at": timezone.now() - timedelta(days=14),
                "ends_at": timezone.now() - timedelta(days=14, hours=-2),
                "location": "Онлайн",
                "organizer": "MAX Library",
                "cover": "https://cdn.example.com/demo/academic-writing.jpg",
                "capacity": 500,
                "remaining": 0,
                "registration_required": False,
                "registration_deadline": None,
                "tags": ["writing", "research"],
                "agenda": [
                    {"time": "17:00", "title": "Основы структуры статьи"},
                    {"time": "18:00", "title": "Ссылки и библиография"},
                ],
                "links": {"recording": "https://events.example.com/writing-webinar"},
                "status": models.EVENT_STATUS_COMPLETED,
                "visibility": "public",
            },
        ]

        campus_events = {}
        for entry in events:
            event, _ = models.CampusEvent.objects.update_or_create(
                id=entry["id"],
                defaults={
                    "title": entry["title"],
                    "subtitle": entry["subtitle"],
                    "description": entry["description"],
                    "category": entry["category"],
                    "starts_at": entry["starts_at"],
                    "ends_at": entry["ends_at"],
                    "location": entry["location"],
                    "organizer": entry["organizer"],
                    "cover": entry["cover"],
                    "capacity": entry["capacity"],
                    "remaining": entry["remaining"],
                    "registration_required": entry["registration_required"],
                    "registration_deadline": entry["registration_deadline"],
                    "visibility": entry.get("visibility", "public"),
                    "tags": entry["tags"],
                    "agenda": entry["agenda"],
                    "links": entry["links"],
                    "status": entry["status"],
                    "meta": {"demo": True},
                },
            )
            campus_events[entry["id"]] = event

        student = self.created.users["student"]
        applicant = self.created.users.get("applicant")
        librarian = self.created.users.get("librarian")
        registration_entries = [
            {
                "event": campus_events["event-max-hackathon"],
                "user": student,
                "status": models.EVENT_REG_STATUS_REGISTERED,
                "form_payload": {"team_name": "CodeMax", "members": 3},
                "ticket": {"qr": "EVENT-QR-123"},
                "check_ins": [{"at": timezone.now().isoformat(), "type": "entrance"}],
                "notifications": {"email": True},
            },
        ]
        if applicant:
            registration_entries.append(
                {
                    "event": campus_events["event-product-meetup"],
                    "user": applicant,
                    "status": models.EVENT_REG_STATUS_WAITLISTED,
                    "form_payload": {"interests": ["product"]},
                    "ticket": {"qr": "PRODUCT-QR-456"},
                    "check_ins": [],
                    "notifications": {"email": True},
                }
            )
        if librarian:
            registration_entries.append(
                {
                    "event": campus_events["event-remote-webinar"],
                    "user": librarian,
                    "status": models.EVENT_REG_STATUS_ATTENDED,
                    "form_payload": {"role": "speaker"},
                    "ticket": {"link": "https://events.example.com/attend"},
                    "check_ins": [{"at": (timezone.now() - timedelta(days=14)).isoformat(), "type": "online"}],
                    "notifications": {"email": True},
                }
            )

        for entry in registration_entries:
            models.EventRegistration.objects.update_or_create(
                event=entry["event"],
                user=entry["user"],
                defaults={
                    "status": entry["status"],
                    "form_payload": entry["form_payload"],
                    "ticket": entry["ticket"],
                    "check_ins": entry["check_ins"],
                    "notifications": entry["notifications"],
                    "metadata": {"demo": True},
                },
            )

        self.log("✓ События кампуса и регистрации добавлены")

    # ----------------------------------------------------------------------- library

    def seed_library(self) -> None:
        catalog_entries = [
            {
                "id": "book-clean-code",
                "title": "Чистый код",
                "subtitle": "Создание, анализ и рефакторинг",
                "authors": ["Роберт Мартин"],
                "publisher": "Питер",
                "published_year": 2021,
                "isbn": "978-5-4461-1234-5",
                "language": "ru",
                "media_type": "book",
                "categories": ["programming"],
                "tags": ["clean code", "refactoring"],
                "description": "Классика разработки ПО, с акцентом на качество кода.",
                "cover_url": "https://cdn.example.com/demo/clean-code.jpg",
                "formats": ["hardcover", "ebook"],
                "availability": {"in_stock": 4},
            },
            {
                "id": "ebook-ml",
                "title": "Machine Learning Engineering",
                "subtitle": "",
                "authors": ["Andriy Burkov"],
                "publisher": "True Positive",
                "published_year": 2020,
                "isbn": "978-2-9995-1234-0",
                "language": "en",
                "media_type": "ebook",
                "categories": ["data"],
                "tags": ["ml", "engineering"],
                "description": "Практическое руководство по построению ML-систем.",
                "cover_url": "https://cdn.example.com/demo/ml-engineering.jpg",
                "formats": ["pdf", "epub"],
                "availability": {"in_stock": 999},
            },
            {
                "id": "magazine-product",
                "title": "Product Management Today",
                "subtitle": "Специальный выпуск про growth-команды",
                "authors": ["Editorial Board"],
                "publisher": "MAX Press",
                "published_year": 2024,
                "isbn": "ISSN-1234-5678",
                "language": "ru",
                "media_type": "magazine",
                "categories": ["product"],
                "tags": ["product", "analytics"],
                "description": "Сборник статей о развитии цифровых продуктов.",
                "cover_url": "https://cdn.example.com/demo/product-magazine.jpg",
                "formats": ["print"],
                "availability": {"in_stock": 12},
            },
            {
                "id": "audiobook-history",
                "title": "History of Space Exploration",
                "subtitle": "From Sputnik to ISS",
                "authors": ["James Walker"],
                "publisher": "Galaxy Audio",
                "published_year": 2019,
                "isbn": "978-1-2345-6789-0",
                "language": "en",
                "media_type": "audiobook",
                "categories": ["science"],
                "tags": ["space", "history"],
                "description": "Аудиокнига о ключевых миссиях в истории космоса.",
                "cover_url": "https://cdn.example.com/demo/space-audio.jpg",
                "formats": ["mp3"],
                "availability": {"in_stock": 100},
            },
        ]

        for entry in catalog_entries:
            item, _ = models.LibraryCatalogItem.objects.update_or_create(
                id=entry["id"],
                defaults={
                    **entry,
                    "meta": {"demo": True},
                },
            )
            self.created.library_items[item.id] = item

        student = self.created.users["student"]
        book = self.created.library_items["book-clean-code"]
        models.LibraryHold.objects.update_or_create(
            item=book,
            user=student,
            pickup_location="Главная библиотека, окно №2",
            defaults={
                "status": "ready",
                "pickup_window": {"from": "2024-06-10", "to": "2024-06-15"},
                "expires_at": timezone.now() + timedelta(days=5),
                "notifications": {"email": True},
                "metadata": {"demo": True},
            },
        )

        magazine = self.created.library_items["magazine-product"]
        models.LibraryHold.objects.update_or_create(
            item=magazine,
            user=student,
            pickup_location="Коворкинг, стойка выдачи журналов",
            defaults={
                "status": models.HOLD_STATUS_PLACED,
                "pickup_window": {"from": "2024-07-01", "to": "2024-07-05"},
                "expires_at": timezone.now() + timedelta(days=2),
                "notifications": {"email": True, "sms": True},
                "metadata": {"demo": True},
            },
        )

        models.LibraryLoan.objects.update_or_create(
            item=book,
            user=student,
            barcode="B123456789",
            defaults={
                "issued_at": timezone.now() - timedelta(days=7),
                "due_at": timezone.now() + timedelta(days=14),
                "status": "active",
                "metadata": {"demo": True},
            },
        )

        models.LibraryLoan.objects.update_or_create(
            item=magazine,
            user=student,
            barcode="M987654321",
            defaults={
                "issued_at": timezone.now() - timedelta(days=20),
                "due_at": timezone.now() - timedelta(days=5),
                "status": models.LOAN_STATUS_OVERDUE,
                "fines": {"amount": "150.00", "currency": "RUB"},
                "metadata": {"demo": True},
            },
        )

        ebook = self.created.library_items["ebook-ml"]
        models.LibraryEBookAccess.objects.update_or_create(
            item=ebook,
            user=student,
            defaults={
                "status": "active",
                "access_url": "https://library.example.com/ebooks/ml",
                "expires_at": timezone.now() + timedelta(days=30),
                "device_limit": 3,
                "drm_info": {"type": "watermark"},
                "metadata": {"demo": True},
            },
        )

        audiobook = self.created.library_items["audiobook-history"]
        models.LibraryEBookAccess.objects.update_or_create(
            item=audiobook,
            user=student,
            defaults={
                "status": models.EBOOK_ACCESS_STATUS_PENDING,
                "access_url": "",
                "expires_at": None,
                "device_limit": 5,
                "drm_info": {"type": "license_pending"},
                "metadata": {"demo": True},
            },
        )

        models.LibraryFinePaymentIntent.objects.update_or_create(
            user=student,
            loan=models.LibraryLoan.objects.get(item=book, user=student),
            defaults={
                "amount": Decimal("350.00"),
                "currency": "RUB",
                "status": models.PAYMENT_INTENT_STATUS_REQUIRES_ACTION,
                "confirmation_url": "https://payments.example.com/confirm/library-fine",
                "provider_payload": {"provider": "demo-pay"},
                "metadata": {"demo": True},
            },
        )

        models.LibraryFinePaymentIntent.objects.update_or_create(
            user=student,
            loan=models.LibraryLoan.objects.get(item=magazine, user=student),
            defaults={
                "amount": Decimal("150.00"),
                "currency": "RUB",
                "status": models.PAYMENT_INTENT_STATUS_PROCESSING,
                "confirmation_url": "https://payments.example.com/confirm/library-magazine",
                "provider_payload": {"provider": "demo-pay"},
                "metadata": {"demo": True},
            },
        )

        self.log("✓ Библиотека: каталог, брони и электронные ресурсы готовы")

    # -------------------------------------------------------------------------- HR

    def seed_hr(self) -> None:
        staff = self.created.users["staff"]
        travel, _ = models.HRTravelRequest.objects.update_or_create(
            user=staff,
            title="Командировка на Digital Forum 2024",
            defaults={
                "purpose": "Выступление с докладом про мини-приложения VK",
                "destination": {"city": "Казань", "country": "Россия"},
                "start_date": date.today() + timedelta(days=15),
                "end_date": date.today() + timedelta(days=18),
                "transport": {"type": "train", "class": "купе"},
                "accommodations": [
                    {"hotel": "Отель Центральный", "check_in": (date.today() + timedelta(days=15)).isoformat()}
                ],
                "expenses_plan": [{"category": "суточные", "amount": 5000, "currency": "RUB"}],
                "approvals": [{"role": "director", "status": "approved"}],
                "documents": [{"name": "invitation.pdf", "url": "https://files.example.com/invite.pdf"}],
                "audit": {"events": []},
                "status": "approved",
                "metadata": {"demo": True},
            },
        )
        self.created.hr_travel_requests.append(travel)

        models.HRTravelRequest.objects.update_or_create(
            user=staff,
            title="Ведение переговоров с партнёрами в Новосибирске",
            defaults={
                "purpose": "Обсуждение совместных образовательных программ",
                "destination": {"city": "Новосибирск", "country": "Россия"},
                "start_date": date.today() + timedelta(days=35),
                "end_date": date.today() + timedelta(days=39),
                "transport": {"type": "plane", "class": "economy"},
                "accommodations": [
                    {"hotel": "Sky Hotel", "check_in": (date.today() + timedelta(days=35)).isoformat()}
                ],
                "expenses_plan": [{"category": "проживание", "amount": 22000, "currency": "RUB"}],
                "approvals": [{"role": "director", "status": "pending"}],
                "documents": [],
                "audit": {"events": [{"at": timezone.now().isoformat(), "action": "created"}]},
                "status": models.TRAVEL_STATUS_SUBMITTED,
                "metadata": {"demo": True},
            },
        )

        models.HRLeaveRequest.objects.update_or_create(
            user=staff,
            leave_type="vacation",
            start_date=date.today() + timedelta(days=45),
            defaults={
                "end_date": date.today() + timedelta(days=55),
                "replacement": {"full_name": "Максим Иванов", "contacts": "@max_student"},
                "approvals": [{"role": "team lead", "status": "pending"}],
                "notes": {"comment": "Семейный отпуск"},
                "status": "pending",
                "metadata": {"demo": True},
            },
        )

        models.HRLeaveRequest.objects.update_or_create(
            user=staff,
            leave_type="sick_leave",
            start_date=date.today() - timedelta(days=10),
            defaults={
                "end_date": date.today() - timedelta(days=5),
                "replacement": {},
                "approvals": [{"role": "team lead", "status": "approved"}],
                "notes": {"comment": "Предоставлены справки"},
                "status": models.LEAVE_STATUS_APPROVED,
                "metadata": {"demo": True},
            },
        )

        models.OfficeCertificateRequest.objects.update_or_create(
            user=staff,
            certificate_type="Employment",
            defaults={
                "purpose": "Для визового центра",
                "delivery": {"type": "digital", "email": staff.email},
                "status": "prepared",
                "metadata": {"demo": True},
            },
        )

        models.OfficeCertificateRequest.objects.update_or_create(
            user=staff,
            certificate_type="Salary",
            defaults={
                "purpose": "Для банка",
                "delivery": {"type": "paper", "pickup": "Ресепшен офиса"},
                "status": models.CERTIFICATE_STATUS_IN_PROGRESS,
                "metadata": {"demo": True},
            },
        )

        models.OfficeGuestPass.objects.update_or_create(
            host=staff,
            guest_full_name="Алексей Иванов",
            visit_date=date.today() + timedelta(days=5),
            defaults={
                "guest_company": "Partner LLC",
                "visit_time_from": "10:00",
                "visit_time_to": "13:00",
                "notes": "Встреча по интеграции",
                "status": "approved",
                "qr_payload": {"code": "OFFICE-QR-001"},
            },
        )

        models.OfficeGuestPass.objects.update_or_create(
            host=staff,
            guest_full_name="Мария Петрова",
            visit_date=date.today() - timedelta(days=3),
            defaults={
                "guest_company": "Digital Agency",
                "visit_time_from": "14:00",
                "visit_time_to": "17:00",
                "notes": "Подписание договора",
                "status": models.OFFICE_GUEST_STATUS_USED,
                "qr_payload": {"code": "OFFICE-QR-042"},
            },
        )

        self.log("✓ HR-процессы и гостевые пропуска заполнены")

    # ---------------------------------------------------------------- dashboards

    def seed_dashboards_news(self) -> None:
        snapshot_date = date.today() - timedelta(days=1)
        models.DashboardSnapshot.objects.update_or_create(
            slug="students_overview",
            date=snapshot_date,
            defaults={
                "scope": "campus",
                "data": {
                    "total_students": 5200,
                    "active_projects": 38,
                    "elective_enrollments": 1240,
                },
                "generated_at": timezone.now(),
                "source": "analytics-pipeline",
                "meta": {"demo": True},
            },
        )

        models.DashboardSnapshot.objects.update_or_create(
            slug="career_applications",
            date=snapshot_date,
            defaults={
                "scope": {"department": "career_center"},
                "data": {
                    "vacancies_open": 12,
                    "applications_new": 34,
                    "applications_in_review": 18,
                },
                "generated_at": timezone.now(),
                "source": "career-analytics",
                "meta": {"demo": True},
            },
        )

        models.NewsMention.objects.update_or_create(
            url="https://news.example.com/articles/max-campus-2024",
            defaults={
                "query": "MAX Campus",
                "source": "TechNews",
                "title": "MAX Campus запускает новые цифровые сервисы для студентов",
                "excerpt": "Платформа расширяет функциональность мини-приложения и внедряет рекомендательную систему.",
                "published_at": timezone.now() - timedelta(days=2),
                "tonality": "positive",
                "reach": 120000,
                "metadata": {"demo": True},
            },
        )

        models.NewsMention.objects.update_or_create(
            url="https://press.example.com/reports/max-campus-growth",
            defaults={
                "query": "MAX Campus",
                "source": "PressDaily",
                "title": "MAX Campus расширяет партнёрства с университетами",
                "excerpt": "Новые соглашения позволят увеличить число международных программ.",
                "published_at": timezone.now() - timedelta(days=5),
                "tonality": "neutral",
                "reach": 85000,
                "metadata": {"demo": True},
            },
        )

        self.log("✓ Дашборды и медиаменшины готовы")

    # ---------------------------------------------------------------- integrations

    def seed_integrations(self) -> None:
        now = timezone.now()
        models.AccessControlEvent.objects.update_or_create(
            device_id="turnstile-1",
            subject_id="ext-100500",
            occurred_at=now.replace(hour=9, minute=5, second=0, microsecond=0),
            defaults={
                "direction": "in",
                "payload": {"device_label": "Главный вход"},
                "metadata": {"demo": True},
            },
        )

        models.AccessControlEvent.objects.update_or_create(
            device_id="turnstile-2",
            subject_id="ext-200600",
            occurred_at=now.replace(hour=19, minute=20, second=0, microsecond=0),
            defaults={
                "direction": "out",
                "payload": {"device_label": "Выход из корпуса B"},
                "metadata": {"demo": True},
            },
        )

        models.TrackerWebhookEvent.objects.update_or_create(
            external_id="JIRA-101",
            event_type="issue.updated",
            defaults={
                "project": self.created.projects["recommendation-platform"],
                "payload": {"status": "in_progress", "assignee": "Сергей Петров"},
                "received_at": now,
                "status": "received",
                "metadata": {"demo": True},
            },
        )

        models.TrackerWebhookEvent.objects.update_or_create(
            external_id="ASTRO-5",
            event_type="issue.transitioned",
            defaults={
                "project": self.created.projects["astro-monitoring"],
                "payload": {"status": "done", "resolution": "fixed"},
                "received_at": now,
                "status": "processed",
                "metadata": {"demo": True},
            },
        )

        models.PaymentProviderWebhook.objects.update_or_create(
            intent_id="tuition-demo",
            defaults={
                "event_type": "payment.succeeded",
                "payload": {"amount": "120000.00", "currency": "RUB"},
                "received_at": now,
                "status": "processed",
                "metadata": {"demo": True},
            },
        )

        models.PaymentProviderWebhook.objects.update_or_create(
            intent_id="tuition-demo-failed",
            defaults={
                "event_type": "payment.failed",
                "payload": {"amount": "15000.00", "currency": "RUB", "reason": "insufficient_funds"},
                "received_at": now - timedelta(hours=2),
                "status": "pending",
                "metadata": {"demo": True},
            },
        )

        models.MaxBotWebhook.objects.update_or_create(
            update_type="message",
            payload={"chat_id": 12345, "text": "Привет!"},
            defaults={
                "user": self.created.users["student"],
                "received_at": now,
                "status": "processed",
                "metadata": {"demo": True},
            },
        )

        models.MaxBotWebhook.objects.update_or_create(
            update_type="callback",
            payload={"chat_id": 67890, "data": "open_schedule"},
            defaults={
                "user": self.created.users["staff"],
                "received_at": now,
                "status": "received",
                "metadata": {"demo": True},
            },
        )

        self.log("✓ Данные интеграций созданы")

    # ------------------------------------------------------------------- main run

    @transaction.atomic
    def run(self) -> None:
        self.seed_universities()
        self.seed_programs()
        self.seed_academic_groups()
        self.seed_users()
        self.seed_teachers_courses_and_lessons()
        self.seed_open_days_and_inquiries()
        self.seed_projects()
        self.seed_career_data()
        self.seed_deanery_data()
        self.seed_dorm_data()
        self.seed_events()
        self.seed_library()
        self.seed_hr()
        self.seed_dashboards_news()
        self.seed_integrations()
        self.log("🎉 База данных успешно заполнена демонстрационными данными")


class Command(BaseCommand):
    help = "Заполнить базу данных правдоподобными демонстрационными данными для всех доменов API."

    def handle(self, *args, **options) -> None:
        seeder = DemoSeeder(self)
        seeder.run()


