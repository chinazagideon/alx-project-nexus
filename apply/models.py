from django.db import models
from job.models import Job
from user.models import User
from upload.models import Upload
# Create your models here.
class ApplicationStatus(models.TextChoices):
    """
    Application status for the job portal
    """
    APPLIED = 'applied', 'Applied'
    INTERVIEW = 'interview', 'Interview'
    APPROVED = 'approved', 'Approved'
    PENDING = 'pending', 'Pending'
    REJECTED = 'rejected', 'Rejected'

class Application(models.Model):
    """
    Application model for the job portal
    """
    job_id = models.ForeignKey(Job, on_delete=models.CASCADE, null=False, blank=False)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    status = models.CharField(max_length=30, choices=ApplicationStatus.choices, default=ApplicationStatus.APPLIED)
    date_applied = models.DateTimeField(auto_now_add=True)
    cover_letter = models.TextField(null=True, blank=True)
    upload_id = models.ForeignKey(Upload, on_delete=models.CASCADE, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.job_id.title