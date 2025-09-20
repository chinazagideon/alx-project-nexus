"""
Serializers for the upload app
"""
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from .models import Upload

class UploadSerializer(serializers.ModelSerializer):
    """
    Serializer for the upload model
    """
    uploaded_by = serializers.PrimaryKeyRelatedField(read_only=True)
    content_type = serializers.SlugRelatedField(slug_field="model", queryset=ContentType.objects.all())

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
        )
        read_only_fields = ("created_at", "uploaded_by", "content_type")
        required_fields = ("file_path", "name", "type")

    def validate(self, attrs):
        """
        Validate the upload data
        """
        request = self.context.get("request")
        uploaded_by = request.user if request else None
        content_type = attrs.get("content_type")
        object_id = attrs.get("object_id")
        return attrs