"""
Application  Serializers
"""

from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from application.models import Application, ApplicationStatus
from job.serializers import JobSerializer
from upload.models import Upload, UploadType
from upload.serializers import UploadSerializer
from user.models.models import User, UserRole
from user.serializers import UserSerializer


class ApplicationSerializer(serializers.ModelSerializer):
    """
    Serializer for the application model
    Backward compatible - resume attachment is optional
    """

    job_details = JobSerializer(source="job", read_only=True)
    user_details = UserSerializer(source="user", read_only=True)
    resume_details = serializers.SerializerMethodField()
    resume = serializers.PrimaryKeyRelatedField(
        queryset=Upload.objects.all(),
        required=False,
        allow_null=True,
        help_text="Optional resume upload ID. If not provided, will automatically attach user's most recent resume.",
    )

    class Meta:
        model = Application
        fields = (
            "id",
            "job",
            "job_details",
            "user",
            "user_details",
            "status",
            "date_applied",
            "cover_letter",
            "updated_at",
            "resume",
            "resume_details",
        )

        read_only_fields = ("updated_at", "status", "date_applied", "id")
        required_fields = ("job", "user")

    def get_resume_details(self, obj):
        """Get the resume details for the application"""
        if obj.resume:
            return UploadSerializer(obj.resume).data
        return None

    def create(self, validated_data):
        """
        Create application with optional resume attachment
        Maintains backward compatibility - resume attachment is optional
        """
        user = validated_data.get("user")
        job = validated_data.get("job")

        # Only attach resume if not explicitly provided in the data
        if "resume" not in validated_data:
            # Find user's most recent resume
            resume = self._get_user_resume(user)
            validated_data["resume"] = resume

        # Create application
        application = Application.objects.create(**validated_data)

        return application

    def _get_user_resume(self, user):
        """
        Get the user's most recent resume upload
        Returns None if no resume found
        """
        try:
            # Find the most recent resume upload for this user
            resume = Upload.objects.filter(uploaded_by=user, type=UploadType.RESUME).order_by("-created_at").first()

            return resume
        except Exception:
            # If any error occurs, return None (no resume)
            return None


class ApplicationCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating applications with enhanced resume handling
    Backward compatible - extends ApplicationSerializer functionality
    """

    job_details = JobSerializer(source="job", read_only=True)
    user_details = UserSerializer(source="user", read_only=True)
    resume_details = serializers.SerializerMethodField()
    resume_attached = serializers.SerializerMethodField()
    resume = serializers.PrimaryKeyRelatedField(
        queryset=Upload.objects.all(),
        required=False,
        allow_null=True,
        help_text="Optional resume upload ID. If not provided, will automatically attach user's most recent resume.",
    )

    class Meta:
        model = Application
        fields = (
            "id",
            "job",
            "job_details",
            "user",
            "user_details",
            "status",
            "date_applied",
            "cover_letter",
            "updated_at",
            "resume",
            "resume_details",
            "resume_attached",
        )
        read_only_fields = ("updated_at", "status", "date_applied", "id")

    def get_resume_details(self, obj):
        """Get the resume details for the application"""
        if obj.resume:
            return UploadSerializer(obj.resume).data
        return None

    def get_resume_attached(self, obj):
        """Check if a resume was attached to the application"""
        return obj.resume is not None

    def create(self, validated_data):
        """
        Create application and automatically attach user's resume
        """
        user = validated_data.get("user")
        job = validated_data.get("job")

        # Find user's most recent resume
        resume = self._get_user_resume(user)

        # Create application with resume
        application = Application.objects.create(**validated_data, resume=resume)

        return application

    def _get_user_resume(self, user):
        """
        Get the user's most recent resume upload
        Returns None if no resume found
        """
        try:
            # Find the most recent resume upload for this user
            resume = Upload.objects.filter(uploaded_by=user, type=UploadType.RESUME).order_by("-created_at").first()

            return resume
        except Exception:
            # If any error occurs, return None (no resume)
            return None


class ApplicationUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating applications (admin/recruiter use)
    """

    job_details = JobSerializer(source="job", read_only=True)
    user_details = UserSerializer(source="user", read_only=True)
    resume_details = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = (
            "id",
            "job_details",
            "user_details",
            "status",
            "date_applied",
            "cover_letter",
            "updated_at",
            "resume_details",
        )
        read_only_fields = ("updated_at", "date_applied", "id")

    def get_resume_details(self, obj):
        """Get the resume details for the application"""
        if obj.resume:
            return UploadSerializer(obj.resume).data
        return None


class ApplicationStatusUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer specifically for updating application status (recruiter/admin use)
    """

    job_details = JobSerializer(source="job", read_only=True)
    user_details = UserSerializer(source="user", read_only=True)
    resume_details = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = (
            "id",
            "job_details",
            "user_details",
            "status",
            "date_applied",
            "cover_letter",
            "updated_at",
            "resume_details",
        )
        read_only_fields = ("updated_at", "date_applied", "id", "cover_letter")

    def get_resume_details(self, obj):
        """Get the resume details for the application"""
        if obj.resume:
            return UploadSerializer(obj.resume).data
        return None


class ApplicationStatusUpdateRequestSerializer(serializers.Serializer):
    """
    Request serializer for updating application status
    """

    status = serializers.ChoiceField(choices=ApplicationStatus.choices, help_text="New status for the application")
