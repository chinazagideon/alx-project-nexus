
"""
Application  Serializers
"""

from rest_framework import serializers
from user.models.models import User
from user.models.models import UserRole
from application.models import Application
from job.serializers import JobSerializer
from user.serializers import UserSerializer


class ApplicationSerializer(serializers.ModelSerializer):
    """
    Serializer for the application model
    """
    job_details = JobSerializer(source='job', read_only=True)
    user_details = UserSerializer(source='user', read_only=True)

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
            "updated_at"
        )
        

        read_only_fields = ("updated_at", "status", "date_applied", "id")
        required_fields = ("job", "user")
