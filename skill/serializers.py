"""
Serializers for the skill app
"""
from rest_framework import serializers
from drf_spectacular.utils import extend_schema
from .models import Skill, JobSkill, UserSkill


class SkillSerializer(serializers.ModelSerializer):
    """
    Serializer for the skill model
    """
    class Meta:
        model = Skill
        fields = ("id", "name")
        # read_only_fields = ("id")

class JobSkillSerializer(serializers.ModelSerializer):
    """
    Serializer for the job skill model
    """
    
    class Meta:
        model = JobSkill
        fields = ("id", "job", "skill")
        # read_only_fields = ("id")
        

class UserSkillSerializer(serializers.ModelSerializer):
    """
    Serializer for the user skill model
    """ 
    class Meta:
        model = UserSkill
        fields = ("id", "user", "skill")
        # read_only_fields = ("id")