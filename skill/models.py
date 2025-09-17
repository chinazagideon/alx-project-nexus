from django.db import models
from job.models import Job
from user.models import User

class Skill(models.Model):
    """
    Skill model for the job portal
    """
    name = models.CharField(max_length=255, null=False, blank=False, unique=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class JobSkill(models.Model):
    """
    Job skill model for the job portal
    """
    job_id = models.ForeignKey(Job, on_delete=models.CASCADE, null=False, blank=False)
    skill_id = models.ForeignKey(Skill, on_delete=models.CASCADE, null=False, blank=False)

    def __str__(self):
        return self.job_id.title
        
class UserSkill(models.Model):
    """
    User skill model for the job portal
    """
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    skill_id = models.ForeignKey(Skill, on_delete=models.CASCADE, null=False, blank=False)

    def __str__(self):
        return self.user_id.username