"""
Skill views
"""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from core.pagination import DefaultPagination
from .models import Skill, JobSkill, UserSkill
from .serializers import SkillSerializer, JobSkillSerializer, UserSkillSerializer
from drf_spectacular.utils import extend_schema
from drf_spectacular.types import OpenApiTypes


class SkillViewSet(viewsets.ModelViewSet):
    """
    Viewset for the skill model
    """

    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [IsAuthenticated]
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

    # @extend_schema(
    #     operation_id="job_skill",
    #     summary="Create Job Skill",
    #     description="Create Job Skill",
    #     tags=["Job Skill"],
    #     request=JobSkillSerializer,
    #     responses={
    #         200: JobSkillSerializer,
    #         400: OpenApiTypes.OBJECT,
    #     },
    # )
    # def create(self, request, *args, **kwargs):
    #     """
    #     Create a new job skill
    #     """
    #     return super().create(request, *args, **kwargs)

    # @extend_schema(
    #     operation_id="job_skill",
    #     summary="List Skills (Job)",
    #     description="Create Job Skill",
    #     tags=["Job Skill"],
    #     request=JobSkillSerializer,
    #     responses={
    #         200: JobSkillSerializer,
    #         400: OpenApiTypes.OBJECT,
    #     },
    # )
    # def list(self, request, *args, **kwargs):
    #     """
    #     Create a new job skill
    #     """
    #     return super().list(request, *args, **kwargs)

    # @extend_schema(
    #     operation_id="job_skill",
    #     summary="Delete Job Skill",
    #     description="Delete Job Skill",
    #     tags=["Job Skill"],
    #     request=JobSkillSerializer,
    # )
    # def destroy(self, request, *args, **kwargs):
    #     """
    #     Delete a job skill
    #     """
    #     return super().destroy(request, *args, **kwargs)


class UserSkillViewSet(viewsets.ModelViewSet):
    """
    Viewset for user skill model: UserSkill related to User model
    """

    queryset = UserSkill.objects.all()
    serializer_class = UserSkillSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPagination

    def get_queryset(self):
        """
        Get the queryset for the user skill list
        """
        return super().get_queryset()

    # @extend_schema(
    #     operation_id="user_skill",
    #     summary="Add Skill (User)",
    #     description="Create User Skill",
    #     tags=["User Skill"],
    #     request=UserSkillSerializer,
    #     responses={
    #         200: UserSkillSerializer,
    #         400: OpenApiTypes.OBJECT,
    #     },
    # )
    # def create(self, request, *args, **kwargs):
    #     """
    #     Add a skill to user
    #     """
    #     return super().create(request, *args, **kwargs)

    # @extend_schema(
    #     operation_id="user_skill",
    #     summary="List User Skill",
    #     description="List User Skill",
    #     tags=["User Skill"],
    #     request=UserSkillSerializer,
    #     responses={
    #         200: UserSkillSerializer,
    #         400: OpenApiTypes.OBJECT,
    #     },
    # )
    # def list(self, request, *args, **kwargs):
    #     """
    #     List all user skills
    #     """
    #     return super().list(request, *args, **kwargs)
