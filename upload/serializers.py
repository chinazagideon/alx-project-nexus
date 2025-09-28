"""
Serializers for the upload app
"""

import os

from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from .models import Upload, UploadType


class UploadSerializer(serializers.ModelSerializer):
    """
    Serializer for the upload model
    """

    uploaded_by = serializers.PrimaryKeyRelatedField(read_only=True)
    content_type = serializers.SlugRelatedField(slug_field="model", queryset=ContentType.objects.all(), required=False)
    file_size = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()

    # Override file_path to handle file uploads properly
    file_path = serializers.FileField(required=True)

    class Meta:
        """
        Meta class for the upload serializer
        """

        model = Upload
        fields = (
            "id",
            "file_path",
            "name",
            "thumbnail",
            "uploaded_by",
            "content_type",
            "object_id",
            "type",
            "created_at",
            "file_size",
            "file_url",
            "thumbnail_url",
        )
        read_only_fields = ("created_at", "uploaded_by", "file_size", "file_url", "thumbnail_url", "content_type", "object_id")

    def get_file_size(self, obj):
        """Get file size in bytes"""
        try:
            if obj.file_path and hasattr(obj.file_path, "size"):
                return obj.file_path.size
        except (FileNotFoundError, OSError, AttributeError):
            # File doesn't exist or other file system error - fail silently
            pass
        return None

    def get_file_url(self, obj):
        """Get full URL for the file"""
        if obj.file_path:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.file_path.url)
            return obj.file_path.url
        return None

    def get_thumbnail_url(self, obj):
        """Get full URL for the thumbnail"""
        if obj.thumbnail:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.thumbnail.url)
            return obj.thumbnail.url
        return None

    def validate_name(self, value):
        """Validate file name"""
        try:
            if not value:
                raise serializers.ValidationError("File name is required")

            # Ensure value is a string
            if not isinstance(value, str):
                raise serializers.ValidationError("File name must be a string")

            # Check file extension
            allowed_extensions = ["pdf", "doc", "docx", "txt", "csv", "xls", "xlsx", "ppt", "pptx"]
            try:
                file_ext = os.path.splitext(value)[1][1:].lower()
            except (IndexError, AttributeError):
                raise serializers.ValidationError("Invalid file name format")

            if file_ext not in allowed_extensions:
                raise serializers.ValidationError(
                    f"File extension '{file_ext}' is not allowed. Allowed extensions: {', '.join(allowed_extensions)}"
                )

            return value
        except Exception as e:
            raise serializers.ValidationError(f"Error validating name: {str(e)}")

    def validate_type(self, value):
        """Validate upload type"""
        if value not in [choice[0] for choice in UploadType.choices]:
            raise serializers.ValidationError(
                f"Invalid upload type. Allowed types: {', '.join([choice[0] for choice in UploadType.choices])}"
            )
        return value

    def create(self, validated_data):
        """
        Create a new upload instance
        """
        request = self.context.get("request")
        if request and hasattr(request, "user") and request.user.is_authenticated:
            validated_data["uploaded_by"] = request.user

            # Set default content_type to user if not provided
            if "content_type" not in validated_data:
                validated_data["content_type"] = ContentType.objects.get_for_model(request.user)
                validated_data["object_id"] = request.user.id
        else:
            raise serializers.ValidationError("User must be authenticated to upload files")

        return super().create(validated_data)

    def validate(self, attrs):
        """
        Validate the upload data
        """
        try:
            request = self.context.get("request")

            # Set uploaded_by from request user
            if request and hasattr(request, "user") and request.user.is_authenticated:
                attrs["uploaded_by"] = request.user

                # Set default content_type and object_id if not provided
                if "content_type" not in attrs or "object_id" not in attrs:
                    attrs["content_type"] = ContentType.objects.get_for_model(request.user)
                    attrs["object_id"] = request.user.id
            else:
                raise serializers.ValidationError("User must be authenticated to upload files")

            return attrs
        except Exception as e:
            raise serializers.ValidationError(f"Error in validate method: {str(e)}")
