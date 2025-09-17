"""
Serializers for the jobs app
"""
from rest_framework import serializers
from .models import Job

class JobSerializer(serializers.ModelSerializer):
    """
    Serializer for the job listing model
    """
    class Meta:
        model = Job
        fields = '__all__'