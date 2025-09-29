from django.shortcuts import render
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from application.models import Application, ApplicationStatus
from application.serializers import (
    ApplicationCreateSerializer,
    ApplicationSerializer,
    ApplicationStatusUpdateRequestSerializer,
    ApplicationStatusUpdateSerializer,
    ApplicationUpdateSerializer,
)
from core.permissions_enhanced import IsAccountActive
from core.response import APIResponse


class ApplicationsViewSet(viewsets.ModelViewSet):
    """
    viewset for application model
    """

    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    # permission_classes = [IsAccountActive]

    def get_serializer_class(self):
        """
        Get the appropriate serializer based on the action
        """
        # Check if enhanced resume handling is requested via query parameter
        use_enhanced = self.request.query_params.get("enhanced_resume", "false").lower() == "true"

        if self.action == "create" and use_enhanced:
            return ApplicationCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return ApplicationUpdateSerializer
        return ApplicationSerializer  # Default for all actions

    # hide the endpoints from docs
    @extend_schema(exclude=True)
    def destroy(self, request, *args, **kwargs):
        """Hide the DELETE endpoint from docs"""
        return super().destroy(request, *args, **kwargs)

    # hide the endpoints from docs
    @extend_schema(exclude=True)
    def update(self, request, *args, **kwargs):
        """Hide the PUT endpoint from docs"""
        return super().update(request, *args, **kwargs)

    # hide the endpoints from docs
    @extend_schema(exclude=True)
    def partial_update(self, request, *args, **kwargs):
        """Hide the PATCH endpoint from docs"""
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        operation_id="application_create",
        summary="Create Job Application",
        description="Create a new job application. Resume is optional - if not provided, will automatically attach user's most recent resume. Use ?enhanced_resume=true for detailed resume information.",
        request=ApplicationSerializer,
        responses={
            201: ApplicationSerializer,
            400: OpenApiTypes.OBJECT,
        },
    )
    def create(self, request, *args, **kwargs):
        """
        Create a new job application
        """

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Set the user to current user if not provided
            if "user" not in serializer.validated_data:
                serializer.validated_data["user"] = request.user

            # Check if user already applied for this job
            job = serializer.validated_data.get("job")
            user = serializer.validated_data.get("user")

            if Application.objects.filter(job=job, user=user).exists():
                return APIResponse.error(
                    message="You have already applied for this job",
                    errors={"job": ["Application already exists for this job"]},
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            application = serializer.save()

            # Enhanced response for resume attachment
            use_enhanced = request.query_params.get("enhanced_resume", "false").lower() == "true"
            if use_enhanced:
                resume_attached = application.resume is not None
                resume_message = (
                    "Resume attached successfully"
                    if resume_attached
                    else "No resume found - application submitted without resume"
                )
                message = f"Application created successfully. {resume_message}"
            else:
                message = "Application created successfully"

            return APIResponse.success(data=serializer.data, message=message, status_code=status.HTTP_201_CREATED)
        else:
            return APIResponse.error(
                message="Failed to create application", errors=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        operation_id="application_update",
        summary="Update Application Status",
        description="Update application status (admin/recruiter only)",
        request=ApplicationUpdateSerializer,
        responses={
            200: ApplicationUpdateSerializer,
            400: OpenApiTypes.OBJECT,
        },
    )
    def update(self, request, *args, **kwargs):
        """
        Update application (admin/recruiter only)
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get("partial", False))

        if serializer.is_valid():
            application = serializer.save()
            return APIResponse.success(
                data=ApplicationUpdateSerializer(application).data,
                message="Application updated successfully",
                status_code=status.HTTP_200_OK,
            )
        else:
            return APIResponse.error(
                message="Failed to update application", errors=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        operation_id="application_update_status",
        summary="Update Application Status",
        description="Update application status (recruiter/admin only). This endpoint allows recruiters and admins to update the status of job applications.",
        request=ApplicationStatusUpdateRequestSerializer,
        responses={
            200: ApplicationStatusUpdateSerializer,
            400: OpenApiTypes.OBJECT,
            403: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
    )
    @action(detail=True, methods=["patch"], url_path="status")
    def update_status(self, request, pk=None):
        """
        Update application status (recruiter/admin only)
        """
        try:
            application = self.get_object()

            # Check if user has permission to update this application
            user = request.user
            if user.role == "recruiter":
                # Recruiters can only update applications for their company's jobs
                if application.job.company.user != user:
                    return APIResponse.error(
                        message="You don't have permission to update this application", status_code=status.HTTP_403_FORBIDDEN
                    )
            elif user.role not in ["admin", "recruiter"]:
                return APIResponse.error(
                    message="Only recruiters and admins can update application status", status_code=status.HTTP_403_FORBIDDEN
                )

            # Validate status
            new_status = request.data.get("status")
            if not new_status:
                return APIResponse.error(
                    message="Status is required",
                    errors={"status": ["This field is required."]},
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            # Validate status choice
            valid_statuses = [choice[0] for choice in ApplicationStatus.choices]
            if new_status not in valid_statuses:
                return APIResponse.error(
                    message="Invalid status",
                    errors={"status": [f"Must be one of: {', '.join(valid_statuses)}"]},
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            # Update the application status
            application.status = new_status
            application.save()

            # Return updated application data
            serializer = ApplicationStatusUpdateSerializer(application)
            return APIResponse.success(
                data=serializer.data, message=f"Application status updated to {new_status}", status_code=status.HTTP_200_OK
            )

        except Application.DoesNotExist:
            return APIResponse.error(message="Application not found", status_code=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return APIResponse.error(
                message="Failed to update application status",
                errors={"detail": [str(e)]},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    def get_queryset(self):
        """
        Get the queryset for applications based on user role:
        - TALENT users see only their own applications
        - RECRUITER users see applications for jobs they own (through their company)
        - ADMIN users see all applications
        """
        user = self.request.user

        if user.role == "admin":
            # Admin can see all applications
            return Application.objects.all()
        elif user.role == "talent":
            # Talent users see only their own applications
            return Application.objects.filter(user=user)
        elif user.role == "recruiter":
            # Recruiters see applications for jobs they own (through their company)
            return Application.objects.filter(job__company__user=user)
        else:
            # Default fallback - return empty queryset for unknown roles
            return Application.objects.none()
