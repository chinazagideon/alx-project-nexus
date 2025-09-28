"""
Models for the job portal
"""

from django.conf import settings
from django.db import models

from address.models import City
from company.models import Company
from job_portal.settings import JOB_CATEGORY_MODEL, JOB_MODEL
from promotion.models import PromotionType, register_promotable


@register_promotable(PromotionType.JOB, "job", "job")
class Job(models.Model):
    """
    Job model for the job portal
    """

    title = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(null=False, blank=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=False, blank=False)
    physical_address = models.JSONField(null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=False, blank=False)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
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

    job = models.ForeignKey(JOB_MODEL, on_delete=models.CASCADE, null=False, blank=False)
    category = models.ForeignKey(JOB_CATEGORY_MODEL, on_delete=models.CASCADE, null=False, blank=False)

    def __str__(self):
        return self.job.title
