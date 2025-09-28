from django.conf import settings
from django.db import models

from job.models import Job
from job_portal.settings import UPLOAD_MODEL


class ApplicationStatus(models.TextChoices):
    """
    Application status for the job portal
    """

    APPLIED = "applied", "Applied"
    INTERVIEW = "interview", "Interview"
    APPROVED = "approved", "Approved"
    PENDING = "pending", "Pending"
    REJECTED = "rejected", "Rejected"


class Application(models.Model):
    """
    Application model for the job portal
    """

    job = models.ForeignKey(Job, on_delete=models.CASCADE, null=False, blank=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False, blank=False)
    status = models.CharField(max_length=30, choices=ApplicationStatus.choices, default=ApplicationStatus.APPLIED)
    date_applied = models.DateTimeField(auto_now_add=True)
    cover_letter = models.TextField(null=False, blank=False)
    resume = models.ForeignKey(UPLOAD_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.job.title
