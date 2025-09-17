"""
Models for the job portal
"""

from django.db import models
from user.models import User
from company.models import Company
from address.models import Address

class Job(models.Model):
    """
    Job model for the job portal
    """
    title = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(null=False, blank=False)
    company_id = models.ForeignKey(Company, on_delete=models.CASCADE, null=False, blank=False)
    address_id = models.ForeignKey(Address, on_delete=models.CASCADE, null=False, blank=False)
    location = models.CharField(max_length=255, null=False, blank=False)
    salary_range = models.CharField(max_length=255, null=False, blank=False)
    date_posted = models.DateTimeField(auto_now_add=True)
    close_date = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Category(models.Model):
    """
    Category model for the job portal
    """
    name = models.CharField(max_length=255, null=False, blank=False)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class JobCategory(models.Model):
    """
    Job category model for the job portal
    """
    job_id = models.ForeignKey('job.Job', on_delete=models.CASCADE, null=False, blank=False)
    category_id = models.ForeignKey('job.Category', on_delete=models.CASCADE, null=False, blank=False)

    def __str__(self):
        return self.job_id.title