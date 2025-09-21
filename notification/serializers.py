from rest_framework import serializers
from .models import Notification, NotificationPreference


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for the notification model
    """
    class Meta:
        """
        Serialize the notification model
        """
        model = Notification
        fields = (
            "id",
            "event_type",
            "title",
            "body",
            "data",
            "status",
            "channels",
            "created_at",
            "read_at",
        )
        read_only_fields = fields


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """
    Serializer for the notification preference model
    """
    class Meta:
        """
        Serialize the notification preference model
        """
        model = NotificationPreference
        fields = (
            "in_app_enabled",
            "email_enabled",
            "push_enabled",
            "quiet_hours_start",
            "quiet_hours_end",
            "timezone",
        )


