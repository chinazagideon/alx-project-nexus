"""
Skill views
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from core.pagination import DefaultPagination
from core.permissions import PublicReadAuthenticatedWrite, IsOwnerOrStaffForList
from .models import Skill, JobSkill, UserSkill
from .serializers import (
    SkillSerializer, 
    JobSkillSerializer, 
    UserSkillSerializer, 
    UserSkillsUpdateSerializer, 
    UserSkillsDeleteSerializer,
    UserSkillsResponseSerializer,
    UserSkillsListResponseSerializer
)
from drf_spectacular.utils import extend_schema, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from enum import Enum
from core.response import APIResponse


class SkillApiEnum(Enum):
    """
    Skill API enum
    """

    user_skill_tag = "User Skill"
    job_skill_tag = "jobs"


class SkillViewSet(viewsets.ModelViewSet):
    """
    Viewset for the skill model
    """

    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [PublicReadAuthenticatedWrite]
    pagination_class = DefaultPagination

    def get_queryset(self):
        """
        Get the queryset for the skill list
        """
        return super().get_queryset()


class JobSkillViewSet(viewsets.ModelViewSet):
    """
    Viewset for job skill model: JobSkill related to Job model
    """

    queryset = JobSkill.objects.all()
    serializer_class = JobSkillSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPagination

    def get_queryset(self):
        """
        Get the queryset for the job skill list
        """
        return super().get_queryset()

    @extend_schema(
        operation_id="job_skill_create",
        summary="Create Job Skill",
        description="Create Job Skill",
        tags=[SkillApiEnum.job_skill_tag.value],
        request=JobSkillSerializer,
        responses={
            200: JobSkillSerializer,
            400: OpenApiTypes.OBJECT,
        },
    )
    def create(self, request, *args, **kwargs):
        """
        Create a new job skill
        """
        return super().create(request, *args, **kwargs)

    @extend_schema(
        operation_id="job_skill_list",
        summary="List Skills (Job)",
        description="Create Job Skill",
        tags=[SkillApiEnum.job_skill_tag.value],
        request=JobSkillSerializer,
        responses={
            200: JobSkillSerializer,
            400: OpenApiTypes.OBJECT,
        },
    )
    def list(self, request, *args, **kwargs):
        """
        Create a new job skill
        """
        return super().list(request, *args, **kwargs)

    @extend_schema(
        operation_id="job_skill_delete",
        summary="Delete Job Skill",
        description="Delete Job Skill",
        tags=[SkillApiEnum.job_skill_tag.value],
        request=JobSkillSerializer,
    )
    def destroy(self, request, *args, **kwargs):
        """
        Delete a job skill
        """
        return super().destroy(request, *args, **kwargs)


class UserSkillViewSet(viewsets.ModelViewSet):
    """
    Viewset for user skill model: UserSkill related to User model
    """

    queryset = UserSkill.objects.all()
    serializer_class = UserSkillSerializer
    permission_classes = [IsOwnerOrStaffForList]
    pagination_class = DefaultPagination

    def get_queryset(self):
        """
        Limit to current user's skills
        """
        if self.request.user.is_staff:
            return UserSkill.objects.all()
        return UserSkill.objects.filter(user=self.request.user)

    @extend_schema(
        operation_id="user_skills_list",
        summary="List current user's skills",
        description="Get all skills associated with the current user",
        tags=[SkillApiEnum.user_skill_tag.value],
        responses={200: UserSkillsListResponseSerializer},
    )
    def list(self, request, *args, **kwargs):
        """
        List current user's skills
        """
        queryset = self.get_queryset()
        serializer = UserSkillSerializer(queryset, many=True)
        skills = serializer.data
        skills_with_user = [{"id": skill["id"], "user": request.user.id, "skill": skill["skill_name"]} for skill in skills]
        return APIResponse.success(
            data=skills_with_user,
            message="User skills listed successfully"
            # status_code=status.HTTP_200_OK
        )

    @extend_schema(
        operation_id="user_skills_add",
        summary="Add skills to current user",
        description="Adds provided skills to the current user (no removal).",
        tags=[SkillApiEnum.user_skill_tag.value],
        request=UserSkillsUpdateSerializer,
        responses={200: UserSkillsResponseSerializer, 400: OpenApiTypes.OBJECT},
        examples=[
            OpenApiExample(
                'Add skills example',
                value={"skills": [1, 2, 3]},
                request_only=True,
            ),
        ],
    )
    def create(self, request, *args, **kwargs):
        """
        Add skills to current user
        """
        ser = UserSkillsUpdateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        skills = ser.validated_data.get('skills', [])
        created = 0
        # create missing pairs
        existing = set(UserSkill.objects.filter(user=request.user, skill_id__in=skills).values_list('skill_id', flat=True))
        to_create = [sid for sid in skills if sid not in existing]
        UserSkill.objects.bulk_create([UserSkill(user=request.user, skill_id=sid) for sid in to_create], ignore_conflicts=True)
        created = len(to_create)
        # return Response({"added": created})
        return APIResponse.success(
            data={"added": created},
            message="User skills added successfully"
        )

    @extend_schema(
        operation_id="user_skills_replace",
        summary="Replace current user's skills",
        description="Sets the user's skills to exactly the provided list (adds missing, removes others).",
        tags=[SkillApiEnum.user_skill_tag.value],
        request=UserSkillsUpdateSerializer,
        responses={200: UserSkillsResponseSerializer, 400: OpenApiTypes.OBJECT},
        examples=[
            OpenApiExample(
                'Replace skills example',
                value={"skills": [2, 4, 5]},
                request_only=True,
            ),
        ],
    )
    def update(self, request, *args, **kwargs):
        """
        Replace current user's skills
        """
        ser = UserSkillsUpdateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        target_ids = set(ser.validated_data.get('skills', []))
        current_ids = set(UserSkill.objects.filter(user=request.user).values_list('skill_id', flat=True))
        to_add = target_ids - current_ids
        to_remove = current_ids - target_ids
        if to_add:
            UserSkill.objects.bulk_create([UserSkill(user=request.user, skill_id=sid) for sid in to_add], ignore_conflicts=True)
        if to_remove:
            UserSkill.objects.filter(user=request.user, skill_id__in=list(to_remove)).delete()
        # return Response({"added": len(to_add), "removed": len(to_remove)})
        return APIResponse.success(
            data={"added": len(to_add), "removed": len(to_remove)},
            message="User skills replaced successfully"
        )
    
    @action(detail=False, methods=['post'], url_path='delete')
    @extend_schema(
        operation_id="user_skills_delete",
        summary="Delete skills from current user",
        description="Deletes the provided skills from the current user.",
        tags=[SkillApiEnum.user_skill_tag.value],
        request=UserSkillsDeleteSerializer,
        responses={200: UserSkillsResponseSerializer, 400: OpenApiTypes.OBJECT},
        examples=[
            OpenApiExample(
                'Delete skills example',
                value={"skills": [1, 3]},
                request_only=True,
            ),
        ],
    )
    def delete_skills(self, request):
        """
        Delete skills from current user
        """
        ser = UserSkillsDeleteSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        skills = ser.validated_data.get('skills', [])
        # Count before deletion
        deleted_count = UserSkill.objects.filter(user=request.user, skill_id__in=skills).count()
        # Delete the skills
        UserSkill.objects.filter(user=request.user, skill_id__in=skills).delete()
        return APIResponse.success(
            data={"deleted": deleted_count},
            message="User skills deleted successfully"
        )
