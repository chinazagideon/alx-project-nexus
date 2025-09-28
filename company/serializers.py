"""
Company serializers
"""

from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import Company


class CompanySerializer(serializers.ModelSerializer):
    """
    Serializer for the company model
    """

    class Meta:
        model = Company
        fields = (
            "id",
            "name",
            "description",
            "user",
            "contact_details",
            "website",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at", "status")


class CompanyCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating companies
    """

    class Meta:
        model = Company
        fields = (
            "id",
            "name",
            "description",
            "contact_details",
            "website",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "status")
