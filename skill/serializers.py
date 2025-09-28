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

    skill_name = serializers.SerializerMethodField()

    def get_skill_name(self, obj):
        return obj.skill.name

    class Meta:
        model = JobSkill
        fields = ("id", "job", "skill", "skill_name")
        # read_only_fields = ("id")


class UserSkillSerializer(serializers.ModelSerializer):
    """
    Serializer for the user skill model
    """

    skill_name = serializers.SerializerMethodField()
    proficiency_display = serializers.SerializerMethodField()

    def get_skill_name(self, obj):
        return obj.skill.name

    def get_proficiency_display(self, obj):
        return obj.get_proficiency_level_display()

    class Meta:
        model = UserSkill
        fields = (
            "id",
            "user",
            "skill",
            "skill_name",
            "proficiency_level",
            "proficiency_display",
            "years_experience",
            "last_used",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "skill_name", "proficiency_display", "user", "created_at", "updated_at")


class UserSkillsUpdateSerializer(serializers.Serializer):
    """
    Serializer to add/replace multiple skills for current user
    """

    skills = serializers.ListField(
        child=serializers.IntegerField(min_value=1), allow_empty=True, help_text="List of skill IDs to add/replace"
    )

    def validate_skills(self, value):
        """Ensure all skill IDs exist and are unique"""
        unique_ids = list(dict.fromkeys(value))
        existing = set(Skill.objects.filter(id__in=unique_ids).values_list("id", flat=True))
        missing = [sid for sid in unique_ids if sid not in existing]
        if missing:
            raise serializers.ValidationError(f"Unknown skill ids: {missing}")
        return unique_ids


class UserSkillsDeleteSerializer(serializers.Serializer):
    """
    Serializer to delete multiple skills for current user
    """

    skills = serializers.ListField(
        child=serializers.IntegerField(min_value=1), allow_empty=False, help_text="List of skill IDs to delete"
    )

    def validate_skills(self, value):
        """Ensure all skill IDs exist and are unique"""
        unique_ids = list(dict.fromkeys(value))
        # Check if skills exist in the Skill model
        existing_skills = set(Skill.objects.filter(id__in=unique_ids).values_list("id", flat=True))
        missing_skills = [sid for sid in unique_ids if sid not in existing_skills]
        if missing_skills:
            raise serializers.ValidationError(f"Unknown skill ids: {missing_skills}")
        return unique_ids


class UserSkillsResponseSerializer(serializers.Serializer):
    """
    Response serializer for user skills operations
    """

    added = serializers.IntegerField(required=False, help_text="Number of skills added")
    removed = serializers.IntegerField(required=False, help_text="Number of skills removed")
    deleted = serializers.IntegerField(required=False, help_text="Number of skills deleted")


class UserSkillsListResponseSerializer(serializers.Serializer):
    """
    Response serializer for listing user skills
    """

    results = UserSkillSerializer(many=True)


# Skill Matching Serializers
class SkillMatchSerializer(serializers.Serializer):
    """
    Serializer for individual skill match
    """

    skill_id = serializers.IntegerField()
    skill_name = serializers.CharField()
    user_proficiency = serializers.IntegerField()
    job_required = serializers.IntegerField()
    match_score = serializers.FloatField()
    status = serializers.CharField()


class MissingSkillSerializer(serializers.Serializer):
    """
    Serializer for missing skills
    """

    skill_id = serializers.IntegerField()
    skill_name = serializers.CharField()
    required_proficiency = serializers.IntegerField()
    importance = serializers.IntegerField()


class SkillAnalysisSerializer(serializers.Serializer):
    """
    Serializer for skill analysis
    """

    matches = SkillMatchSerializer(many=True)
    missing_skills = MissingSkillSerializer(many=True)
    total_required = serializers.IntegerField()
    exact_matches = serializers.IntegerField()
    missing_count = serializers.IntegerField()


class JobRecommendationSerializer(serializers.Serializer):
    """
    Serializer for job recommendations
    """

    job_id = serializers.IntegerField()
    job_title = serializers.CharField()
    company_name = serializers.CharField()
    match_percentage = serializers.FloatField()
    skill_analysis = SkillAnalysisSerializer()
    date_posted = serializers.DateTimeField()
    salary_min = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)
    salary_max = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)


class JobRecommendationsResponseSerializer(serializers.Serializer):
    """
    Response serializer for job recommendations
    """

    recommendations = JobRecommendationSerializer(many=True)
    total_count = serializers.IntegerField()
    min_match_threshold = serializers.FloatField()


class JobSkillMatchResponseSerializer(serializers.Serializer):
    """
    Response serializer for job skill match analysis
    """

    job_id = serializers.IntegerField()
    job_title = serializers.CharField()
    company_name = serializers.CharField()
    user_id = serializers.IntegerField()
    overall_match = serializers.FloatField()
    skill_analysis = SkillAnalysisSerializer()
    recommendations = serializers.ListField(child=serializers.CharField())


class UserSkillProfileSerializer(serializers.Serializer):
    """
    Serializer for user skill profile
    """

    user_id = serializers.IntegerField()
    skills = serializers.ListField()
    skill_demand = serializers.DictField()
    total_skills = serializers.IntegerField()
