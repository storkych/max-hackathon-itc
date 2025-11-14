from django.db.models import Q
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .... import models
from ....serializers import (
    ProjectApplicationCreateSerializer,
    ProjectApplicationSerializer,
    ProjectCreateSerializer,
    ProjectDetailSerializer,
    ProjectSerializer,
    ProjectSubscriptionSerializer,
    ProjectTaskSerializer,
    ProjectTeamMembershipSerializer,
)
from ....utils import parse_init_data_payload


class ProjectListView(ListAPIView):
    serializer_class = ProjectSerializer

    def get_queryset(self):
        params = self.request.query_params
        queryset = models.Project.objects.all().order_by("-created_at")
        q = params.get("q")
        if q:
            queryset = queryset.filter(Q(title__icontains=q) | Q(summary__icontains=q))
        direction = params.getlist("domain")
        if direction:
            queryset = queryset.filter(domain_tags__overlap=direction)
        stack = params.getlist("stack")
        if stack:
            queryset = queryset.filter(skills_required__overlap=stack)
        owner_type = params.get("owner_type")
        if owner_type:
            queryset = queryset.filter(owner_type=owner_type)
        department = params.get("department")
        if department:
            queryset = queryset.filter(department_id=department)
        status_filter = params.get("status") or models.PROJECT_STATUS_APPROVED
        queryset = queryset.filter(status=status_filter)
        return queryset

    def post(self, request, *args, **kwargs):
        serializer = ProjectCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        raw_init_data = request.META.get("HTTP_X_MAX_INIT_DATA")
        if not raw_init_data:
            return Response({"detail": "X-Max-Init-Data header is required."}, status=status.HTTP_401_UNAUTHORIZED)
        init_payload = parse_init_data_payload(raw_init_data)
        user_payload = init_payload.get("user") or {}
        user_id = user_payload.get("id")
        if not user_id:
            return Response({"detail": "Init data does not contain user id."}, status=status.HTTP_400_BAD_REQUEST)
        user_profile = models.UserProfile.objects.filter(user_id=str(user_id)).first()
        if not user_profile:
            return Response({"detail": "User profile not found."}, status=status.HTTP_404_NOT_FOUND)
        if user_profile.role not in {models.UserProfile.ROLE_STUDENT, models.UserProfile.ROLE_STAFF}:
            return Response({"detail": "project_creation_role_not_allowed"}, status=status.HTTP_403_FORBIDDEN)
        department = None
        if data.get("department_id"):
            department = models.Department.objects.filter(id=data["department_id"]).first()
        project = models.Project.objects.create(
            code=f"prj_{models.Project.objects.count() + 1:07d}",
            owner_type=data["owner"]["type"],
            owner_user=user_profile,
            department=department,
            title=data["title"],
            summary=data["summary"],
            description_md=data["description_md"],
            domain_tags=data.get("domain_tags", []),
            skills_required=data.get("skills_required", []),
            format=data.get("constraints", {}).get("format", models.PROJECT_FORMAT_INTRA),
            links=data.get("links", {}),
            timeline=data.get("timeline", {}),
            team=data.get("team", {}),
            constraints=data.get("constraints", {}),
            education=data.get("education", {}),
            contacts=data.get("contacts", {}),
            moderation={
                "required": True,
                "queue_position": 0,
                "sla_hours": 48,
            },
            status=models.PROJECT_STATUS_PENDING,
        )
        return Response(ProjectDetailSerializer(project).data, status=status.HTTP_201_CREATED)


class ProjectDetailView(RetrieveAPIView):
    queryset = models.Project.objects.all()
    lookup_field = "id"
    serializer_class = ProjectDetailSerializer


class ProjectApplyView(APIView):
    def post(self, request, project_id: str):
        project = models.Project.objects.filter(id=project_id).first()
        if not project:
            return Response({"detail": "project_not_found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProjectApplicationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        vacancy = None
        if data.get("role_code"):
            vacancy = models.ProjectVacancy.objects.filter(project=project, role_code=data["role_code"]).first()
        application, created = models.ProjectApplication.objects.get_or_create(
            project=project,
            user=request.user,
            defaults={
                "vacancy": vacancy,
                "motivation": data.get("motivation", ""),
                "attachments": data.get("attachments", []),
                "cv_url": data.get("cv_url") or "",
                "portfolio_url": data.get("portfolio_url") or "",
                "consents": data.get("consents", {}),
            },
        )
        if not created:
            return Response({"detail": "already_applied"}, status=status.HTTP_409_CONFLICT)
        return Response(ProjectApplicationSerializer(application).data, status=status.HTTP_201_CREATED)


class ProjectTeamView(ListAPIView):
    serializer_class = ProjectTeamMembershipSerializer

    def get_queryset(self):
        project_id = self.kwargs["project_id"]
        return models.ProjectTeamMembership.objects.filter(project_id=project_id).select_related("user")


class ProjectTasksView(ListAPIView):
    serializer_class = ProjectTaskSerializer

    def get_queryset(self):
        project_id = self.kwargs["project_id"]
        return models.ProjectTask.objects.filter(project_id=project_id).order_by("due_date")


class ProjectSubscriptionsView(APIView):
    def post(self, request, project_id: str):
        project = models.Project.objects.filter(id=project_id).first()
        if not project:
            return Response({"detail": "project_not_found"}, status=status.HTTP_404_NOT_FOUND)
        subscription, _ = models.ProjectSubscription.objects.get_or_create(
            project=project,
            user=request.user,
            defaults={"channels": ["in_app"]},
        )
        return Response(ProjectSubscriptionSerializer(subscription).data, status=status.HTTP_201_CREATED)

