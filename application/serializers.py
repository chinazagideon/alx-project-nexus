
"""
Application  Serializers
"""

from rest_framework import serializers
from user.models.models import User
from user.models.models import UserRole
from application.models import Application


class ApplicationSerializer(serializers.ModelSerializer):
    """
    Serializer for the application model
    """

    class Meta:
        model = Application
        fields = (
            "job",
            "user", 
            "status",
            "date_applied",
            "cover_letter",
            "updated_at"
        )

        read_only_fields = ("updated_at", "status", "date_applied")
        required_fields = ("job", "user")
