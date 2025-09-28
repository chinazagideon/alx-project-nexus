from django.db import models
from job.models import Job
from django.conf import settings

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
    PROFICIENCY_CHOICES = [
        (1, 'Beginner'),
        (2, 'Novice'),
        (3, 'Intermediate'),
        (4, 'Advanced'),
        (5, 'Expert'),
    ]
    
    IMPORTANCE_CHOICES = [
        (1, 'Nice to have'),
        (2, 'Preferred'),
        (3, 'Important'),
        (4, 'Required'),
        (5, 'Critical'),
    ]
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, null=False, blank=False)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, null=False, blank=False)
    required_proficiency = models.IntegerField(choices=PROFICIENCY_CHOICES, default=1, help_text="Required proficiency level")
    importance = models.IntegerField(choices=IMPORTANCE_CHOICES, default=3, help_text="How important this skill is for the job")
    years_required = models.FloatField(default=0.0, help_text="Years of experience required")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        unique_together = ('job', 'skill')

    def __str__(self):
        return f"{self.job.title} - {self.skill.name} ({self.get_required_proficiency_display()})"
        
class UserSkill(models.Model):
    """
    User skill model for the job portal
    """
    PROFICIENCY_CHOICES = [
        (1, 'Beginner'),
        (2, 'Novice'),
        (3, 'Intermediate'),
        (4, 'Advanced'),
        (5, 'Expert'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False, blank=False)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, null=False, blank=False)
    proficiency_level = models.IntegerField(choices=PROFICIENCY_CHOICES, default=1, help_text="Skill proficiency level (1-5)")
    years_experience = models.FloatField(default=0.0, help_text="Years of experience with this skill")
    last_used = models.DateField(null=True, blank=True, help_text="Last time this skill was used")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        unique_together = ('user', 'skill')

    def __str__(self):
        return f"{self.user.username} - {self.skill.name} ({self.get_proficiency_level_display()})"