"""
Models for the company
"""
from django.db import models
from user.models.models import User
from address.models import Address

class Company(models.Model):
    """
    Company model for the company
    """
    name = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    # address = models.ForeignKey(Address, on_delete=models.CASCADE, null=False, blank=False)
    website = models.URLField(null=True, blank=True)
    contact_details = models.CharField(max_length=255, null=True, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
