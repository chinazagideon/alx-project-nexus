from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from user.models.models import User, UserStatus


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    search_fields = ("username", "email", "first_name", "last_name")
    list_display = ("username", "email", "role", "status", "is_email_verified", "is_active", "is_staff")
    list_filter = ("status", "is_email_verified", "role", "is_active", "is_staff")
    fieldsets = DjangoUserAdmin.fieldsets + ((None, {"fields": ("role", "phone", "status", "is_email_verified")}),)

    actions = ["activate_users", "deactivate_users", "suspend_users"]

    def activate_users(self, request, queryset):
        """Activate selected users"""
        updated = queryset.update(status=UserStatus.ACTIVE, is_email_verified=True)
        self.message_user(request, f"{updated} users activated successfully.", messages.SUCCESS)

    activate_users.short_description = "Activate selected users"

    def deactivate_users(self, request, queryset):
        """Deactivate selected users"""
        updated = queryset.update(status=UserStatus.INACTIVE)
        self.message_user(request, f"{updated} users deactivated successfully.", messages.SUCCESS)

    deactivate_users.short_description = "Deactivate selected users"

    def suspend_users(self, request, queryset):
        """Suspend selected users"""
        updated = queryset.update(status=UserStatus.PENDING)
        self.message_user(request, f"{updated} users suspended successfully.", messages.SUCCESS)

    suspend_users.short_description = "Suspend selected users"
