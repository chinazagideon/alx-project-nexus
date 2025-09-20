from django.db import models
from job.models import Job
from user.models.models import User

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
    job = models.ForeignKey(Job, on_delete=models.CASCADE, null=False, blank=False)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, null=False, blank=False)

    def __str__(self):
        return self.job.title
        
class UserSkill(models.Model):
    """
    User skill model for the job portal
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, null=False, blank=False)

    def __str__(self):
        return self.user.username