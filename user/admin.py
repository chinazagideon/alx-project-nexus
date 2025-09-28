from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from user.models.models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    search_fields = ("username", "email", "first_name", "last_name")
    list_display = ("username", "email", "role", "status", "is_active", "is_staff")
    fieldsets = DjangoUserAdmin.fieldsets + ((None, {"fields": ("role", "phone", "status")}),)
