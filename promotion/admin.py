from django.contrib import admin
from .models import Promotion, PromotionPackage


@admin.register(PromotionPackage)
class PromotionPackageAdmin(admin.ModelAdmin):
    """
    Admin for the promotion package model
    """

    list_display = (
        "name",
        "placement",
        "price",
        "duration_days",
        "priority_weight",
        "is_active",
    )
    list_filter = (
        "placement",
        "is_active",
    )
    search_fields = ("name",)


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    """
    Admin for the promotion model
    """

    list_display = (
        "id",
        "type",
        "owner",
        "content_type",
        "object_id",
        "package",
        "placement",
        "status",
        "start_at",
        "end_at",
        "created_at",
    )

    list_filter = (
        "type",
        "placement",
        "status",
        "content_type",
    )
    search_fields = ("id", "payment_reference")
    autocomplete_fields = ("owner", "approved_by")
