"""
Models for the address
"""
from django.db import models

class Address(models.Model):
    """
    Address model for the address
    """
    location = models.TextField(null=False, blank=False)
    city_id = models.ForeignKey('address.City', on_delete=models.CASCADE, null=False, blank=False)
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
    state_id = models.ForeignKey('address.State', on_delete=models.CASCADE, null=False, blank=False)
    
    def __str__(self):
        return self.name

class State(models.Model):
    """
    State model for the address
    """
    name = models.CharField(max_length=255, null=False, blank=False)
    country_id = models.ForeignKey('address.Country', on_delete=models.CASCADE, null=False, blank=False)

    def __str__(self):
        return self.name