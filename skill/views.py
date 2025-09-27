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
    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        """
        Get the queryset for the job skill list
        """
        return JobSkill.objects.all()

    @extend_schema(
        operation_id="job_skill_create",
        summary="Create Job Skill",
        description="Create Job Skill - Associates a skill with a job posting",
        tags=[SkillApiEnum.job_skill_tag.value],
        request=JobSkillSerializer,
        responses={
            201: JobSkillSerializer,
            400: OpenApiTypes.OBJECT,
        },
    )
    def create(self, request, *args, **kwargs):
        """
        Create a new job skill association
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Check for duplicate job-skill combinations
            job_id = serializer.validated_data['job'].id
            skill_id = serializer.validated_data['skill'].id
            
            if JobSkill.objects.filter(job_id=job_id, skill_id=skill_id).exists():
                return APIResponse.error(
                    message="Job skill association already exists",
                    errors={"detail": f"Job {job_id} already has skill {skill_id} associated"},
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return APIResponse.success(
                data=serializer.data,
                message="Job skill created successfully",
                status_code=status.HTTP_201_CREATED
            )
        else:
            return APIResponse.error(
                message="Failed to create job skill",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

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

    @action(detail=False, methods=['post'], url_path='bulk-create')
    @extend_schema(
        operation_id="job_skills_bulk_create",
        summary="Bulk Create Job Skills",
        description="Create multiple job skill associations at once",
        tags=[SkillApiEnum.job_skill_tag.value],
        request={
            'type': 'object',
            'properties': {
                'job': {'type': 'integer', 'description': 'Job ID'},
                'skills': {
                    'type': 'array',
                    'items': {'type': 'integer'},
                    'description': 'List of skill IDs to associate with the job'
                }
            },
            'required': ['job', 'skills']
        },
        responses={
            201: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                'Bulk create job skills',
                value={"job": 1, "skills": [33, 34, 35]},
                request_only=True,
            ),
        ],
    )
    def bulk_create_skills(self, request):
        """
        Create multiple job skill associations at once
        """
        job_id = request.data.get('job')
        skill_ids = request.data.get('skills', [])
        
        if not job_id:
            return APIResponse.error(
                message="Job ID is required",
                errors={"job": ["This field is required"]},
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        if not skill_ids:
            return APIResponse.error(
                message="At least one skill ID is required",
                errors={"skills": ["This field is required and must not be empty"]},
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate job exists
        from job.models import Job
        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            return APIResponse.error(
                message="Job not found",
                errors={"job": [f"Job with id {job_id} does not exist"]},
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate skills exist
        from skill.models import Skill
        existing_skills = set(Skill.objects.filter(id__in=skill_ids).values_list('id', flat=True))
        missing_skills = [sid for sid in skill_ids if sid not in existing_skills]
        if missing_skills:
            return APIResponse.error(
                message="Some skills not found",
                errors={"skills": [f"Skills with ids {missing_skills} do not exist"]},
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Check for existing associations
        existing_associations = set(
            JobSkill.objects.filter(job_id=job_id, skill_id__in=skill_ids)
            .values_list('skill_id', flat=True)
        )
        
        # Create only new associations
        new_skill_ids = [sid for sid in skill_ids if sid not in existing_associations]
        created_count = 0
        
        if new_skill_ids:
            job_skills = [JobSkill(job_id=job_id, skill_id=skill_id) for skill_id in new_skill_ids]
            JobSkill.objects.bulk_create(job_skills, ignore_conflicts=True)
            created_count = len(new_skill_ids)
        
        return APIResponse.success(
            data={
                "job_id": job_id,
                "created_count": created_count,
                "existing_count": len(existing_associations),
                "total_skills": len(skill_ids)
            },
            message=f"Successfully created {created_count} job skill associations",
            status_code=status.HTTP_201_CREATED
        )


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
