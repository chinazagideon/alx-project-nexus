"""
Models for the address
"""

from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class Address(models.Model):
    """
    Address model for the address
    """

    location = models.TextField(null=False, blank=False)
    city = models.ForeignKey("address.City", on_delete=models.CASCADE, null=False, blank=False)
    state = models.ForeignKey("address.State", on_delete=models.CASCADE, null=False, blank=False)
    country = models.ForeignKey("address.Country", on_delete=models.CASCADE, null=False, blank=False)

    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    content_object = GenericForeignKey("content_type", "object_id")

    zip_code = models.CharField(max_length=20, null=False, blank=False)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.location


class Country(models.Model):
    """
    Country model for the address
    """

    name = models.CharField(max_length=255, null=False, blank=False)
    code = models.CharField(max_length=50, null=False, blank=False, unique=True)

    def __str__(self):
        return self.name


class City(models.Model):
    """
    City model for the address
    """

    name = models.CharField(max_length=255, null=False, blank=False)
    state = models.ForeignKey("address.State", on_delete=models.CASCADE, null=False, blank=False)

    def __str__(self):
        return self.name


class State(models.Model):
    """
    State model for the address
    """

    name = models.CharField(max_length=255, null=False, blank=False)
    country = models.ForeignKey("address.Country", on_delete=models.CASCADE, null=False, blank=False)

    def __str__(self):
        return self.name
