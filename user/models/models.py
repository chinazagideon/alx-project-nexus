from django.db import models
from django.contrib.auth.models import AbstractUser
from enum import Enum
from django.core.validators import validate_email

class UserRole(models.TextChoices):
    """
    User role for the job portal
    """
    ADMIN = 'admin', 'Admin'
    RECRUITER = 'recruiter', 'Recruiter'
    TALENT = 'talent', 'Talent'

class UserStatus(models.TextChoices):
    """
    User status for the job portal
    """
    ACTIVE = 'active', 'Active'
    INACTIVE = 'inactive', 'Inactive'
    PENDING = 'pending', 'Pending'

class User(AbstractUser):
    """
    User model for the job portal
    """
    email = models.EmailField(unique=True, null=False, blank=False, validators=[validate_email])
    first_name = models.CharField(max_length=30, null=False, blank=False)
    last_name = models.CharField(max_length=30, null=False, blank=False)
    username = models.CharField(max_length=30, null=False, blank=False, unique=True)
    role = models.CharField(max_length=30, choices=UserRole.choices, null=False, blank=False)
    phone = models.CharField(max_length=30, null=True, blank=True)
    status = models.CharField(max_length=30, choices=UserStatus.choices, default=UserStatus.PENDING)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'role', 'phone']

    def __str__(self):
        return self.username
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_short_name(self):
        return self.first_name
    
    def get_username(self):
        return self.username
    
    def get_email(self):
        return self.email

    
