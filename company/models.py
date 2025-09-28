"""
Models for the company
"""

from django.conf import settings
from django.db import models

from address.models import Address


class Company(models.Model):
    """
    Company model for the company
    """

    name = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(null=False, blank=False, default="")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False, blank=False)
    # address = models.ForeignKey(Address, on_delete=models.CASCADE, null=False, blank=False)
    website = models.URLField(null=True, blank=True, default="")
    contact_details = models.CharField(max_length=255, null=False, blank=False, default="")
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
