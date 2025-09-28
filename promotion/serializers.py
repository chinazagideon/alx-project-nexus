from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from rest_framework import serializers

from .models import Promotion, PromotionPackage


class PromotionPackageSerializer(serializers.ModelSerializer):
    """
    Serializer for the promotion package model
    """

    class Meta:
        model = PromotionPackage
        fields = (
            "id",
            "name",
            "description",
            "price",
            "duration_days",
            "priority_weight",
            "placement",
            "is_active",
        )


class PromotionSerializer(serializers.ModelSerializer):
    """
    Serializer for the promotion model
    """

    owner = serializers.PrimaryKeyRelatedField(read_only=True)
    package = serializers.PrimaryKeyRelatedField(queryset=PromotionPackage.objects.filter(is_active=True))
    content_type = serializers.SlugRelatedField(slug_field="model", queryset=ContentType.objects.all())

    class Meta:
        model = Promotion
        fields = (
            "id",
            "owner",
            "type",
            "content_type",
            "object_id",
            "package",
            "placement",
            "start_at",
            "end_at",
            "status",
            "payment_reference",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("status", "created_at", "updated_at")

    def validate(self, attrs):
        """
        Validate the promotion data
        """
        request = self.context.get("request")
        owner = request.user if request else None
        content_type = attrs.get("content_type")
        object_id = attrs.get("object_id")
        promo_type = attrs.get("type")
        package = attrs.get("package")

        # whitelist models for each type
        model_class = content_type.model_class()
        if not hasattr(model_class, "_promotion_types"):
            raise serializers.ValidationError("Model is not promotable")

        # check if the model is promotable
        if (promo_type, content_type.app_label, content_type.model) not in model_class._promotion_types:
            raise serializers.ValidationError(
                f"Model {content_type.app_label}.{content_type.model} " f"cannot be promoted as {promo_type}"
            )

        # check if the placement matches the package's placement
        if package and attrs.get("placement") and package.placement != attrs["placement"]:
            raise serializers.ValidationError("Placement must match the package's placement.")

        # break out of the validation
        return attrs

        # set start/end if absent
        now = timezone.now()
        start_at = attrs.get("start_at") or now
        end_at = attrs.get("end_at") or (start_at + timezone.timedelta(days=package.duration_days))
        if end_at <= start_at:
            raise serializers.ValidationError("end_at must be after start_at")

        # set the start and end dates
        attrs["start_at"] = start_at
        attrs["end_at"] = end_at

        # check if there is already an active promotion for this object
        if Promotion.objects.active(now=now).filter(content_type=content_type, object_id=object_id).exists():
            raise serializers.ValidationError("There is already an active promotion for this object.")

        # check if the owner controls the target object
        if owner != model_class.objects.get(id=object_id).owner:
            raise serializers.ValidationError("Owner does not control the target object.")

        # break out of the validation
        return attrs

    def create(self, validated_data):
        """
        Create a new promotion
        """
        request = self.context.get("request")
        owner = request.user if request else None
        validated_data["owner"] = owner
        # default placement from package if not provided
        if not validated_data.get("placement"):
            validated_data["placement"] = validated_data["package"].placement
        # return the created promotion
        return super().create(validated_data)
