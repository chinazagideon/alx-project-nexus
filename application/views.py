from django.shortcuts import render
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from application.models import Application
from application.serializers import ApplicationCreateSerializer, ApplicationSerializer, ApplicationUpdateSerializer
from core.permissions_enhanced import IsAccountActive
from core.response import APIResponse


class ApplicationsViewSet(viewsets.ModelViewSet):
    """
    viewset for application model
    """

    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [IsAccountActive]

    def get_serializer_class(self):
        """
        Return appropriate serializer based on action
        Maintains backward compatibility by defaulting to ApplicationSerializer
        Enhanced serializers are used only when explicitly needed
        """
        # Check if enhanced resume handling is requested via query parameter
        use_enhanced = self.request.query_params.get("enhanced_resume", "false").lower() == "true"

        if self.action == "create" and use_enhanced:
            return ApplicationCreateSerializer
        elif self.action in ["update", "partial_update"] and use_enhanced:
            return ApplicationUpdateSerializer
        return ApplicationSerializer  # Default for all actions - backward compatible

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
        Backward compatible - enhanced resume handling is optional
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

            # Enhanced response for resume attachment (backward compatible)
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
