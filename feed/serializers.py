from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType

from .models import FeedItem
from company.models import Company
from promotion.models import Promotion
from job.models import Job


class FeedPayloadField(serializers.Field):
    """
    Field to serialize the payload of a feed item
    """
    def to_representation(self, feed_item: FeedItem):
        """
        Serialize the payload of a feed item
        """
        model = feed_item.content_type.model
        obj = feed_item.content_object
        if feed_item.event_type == FeedItem.EVENT_JOB_POSTED and isinstance(obj, Job):
            return {
                "type": "job",
                "job": {
                    "id": obj.id,
                    "title": getattr(obj, "title", None),
                    "company_name": getattr(getattr(obj, "company", None), "name", None),
                    "location": getattr(obj, "physical_address", None),
                    "city": getattr(obj, "city_name", None),
                    "salary_min": getattr(obj, "salary_min", None),
                    "salary_max": getattr(obj, "salary_max", None),
                    "date_posted": getattr(obj, "date_posted", None),
                },
            }
        if feed_item.event_type == FeedItem.EVENT_COMPANY_JOINED and isinstance(obj, Company):
            return {
                "type": "company",
                "company": {
                    "id": obj.id,
                    "name": getattr(obj, "name", None),
                    "created_at": getattr(obj, "created_at", None),
                },
            }
        if feed_item.event_type == FeedItem.EVENT_PROMOTION_ACTIVE and isinstance(obj, Promotion):
            return {
                "type": "promotion",
                "promotion": {
                    "id": obj.id,
                    "type": getattr(obj, "type", None),
                    "package_id": getattr(obj, "package_id", None),
                    "target": {
                        "content_type": obj.content_type.model if getattr(obj, "content_type", None) else None,
                        "object_id": getattr(obj, "object_id", None),
                    },
                },
            }
        return {"type": "unknown"}


class FeedItemSerializer(serializers.ModelSerializer):
    """
    Serializer for the feed item model
    """
    payload = FeedPayloadField(source="*")

    class Meta:
        model = FeedItem
        fields = (
            "id",
            "event_type",
            "created_at",
            "score",
            "payload",
        )


class FeedListResponseSerializer(serializers.Serializer):
    """
    Serializer for the feed list response
    """
    results = FeedItemSerializer(many=True)
    next_cursor = serializers.CharField(allow_null=True)


