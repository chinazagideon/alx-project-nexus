"""
Serializers for the jobs app
"""

from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models import Case, CharField, F, Q, Value, When
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from skill.models import JobSkill, Skill

from .models import Category, Job, JobCategory


# Job serializer
class JobSerializer(serializers.ModelSerializer):
    """
    Serializer for the job listing model
    """

    company_name = serializers.CharField(source="company.name", read_only=True)
    company_description = serializers.CharField(source="company.description", read_only=True)
    city_name = serializers.CharField(source="city.name", read_only=True)
    # address_city = serializers.CharField(source='address.city', read_only=True)
    city_state = serializers.CharField(source="city.state.name", read_only=True)
    state_country = serializers.CharField(source="city.state.country.name", read_only=True)
    categories = serializers.SerializerMethodField()
    skills = serializers.SerializerMethodField()
    is_promoted = serializers.BooleanField(read_only=True)
    promotion_priority = serializers.IntegerField(read_only=True)

    class Meta:
        """
        Meta class for the job serializer
        """

        model = Job
        fields = (
            "id",
            "title",
            "description",
            "company",
            "company_name",
            "company_description",
            "physical_address",
            "city",
            "city_name",
            "city_state",
            "state_country",
            "salary_min",
            "salary_max",
            "date_posted",
            "close_date",
            "updated_at",
            "categories",
            "skills",
            "is_promoted",
            "promotion_priority",
        )
        read_only_fields = ("date_posted", "close_date")

    @extend_schema_field(serializers.ListField(child=serializers.CharField()))
    def get_categories(self, obj):
        """Get job categories"""
        return [cat.category.name for cat in obj.jobcategory_set.all()]

    @extend_schema_field(serializers.ListField(child=serializers.DictField()))
    def get_skills(self, obj):
        """Get job skills with ID and name"""
        return [{"id": job_skill.skill.id, "name": job_skill.skill.name} for job_skill in obj.jobskill_set.all()]


# Job create serializer with skills support
class JobCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating jobs with skills support
    """

    skills = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False,
        allow_empty=True,
        help_text="List of skill IDs to associate with the job",
    )

    class Meta:
        """
        Meta class for the job create serializer
        """

        model = Job
        fields = (
            "id",
            "title",
            "description",
            "company",
            "physical_address",
            "city",
            "salary_min",
            "salary_max",
            "close_date",
            "skills",
        )
        read_only_fields = ("id",)

    def validate_skills(self, value):
        """Validate that all skill IDs exist and are unique"""
        if not value:
            return value

        unique_ids = list(dict.fromkeys(value))
        existing_skills = set(Skill.objects.filter(id__in=unique_ids).values_list("id", flat=True))
        missing_skills = [sid for sid in unique_ids if sid not in existing_skills]

        if missing_skills:
            raise serializers.ValidationError(f"Unknown skill ids: {missing_skills}")

        return unique_ids

    def create(self, validated_data):
        """Create job and associate skills"""
        skills_data = validated_data.pop("skills", [])
        job = Job.objects.create(**validated_data)

        # Create JobSkill relationships
        for skill_id in skills_data:
            JobSkill.objects.create(job=job, skill_id=skill_id)

        return job

    def update(self, instance, validated_data):
        """Update job and skills"""
        skills_data = validated_data.pop("skills", None)

        # Update job fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update skills if provided
        if skills_data is not None:
            # Remove existing skills
            JobSkill.objects.filter(job=instance).delete()

            # Add new skills
            for skill_id in skills_data:
                JobSkill.objects.create(job=instance, skill_id=skill_id)

        return instance


# Search request serializer
class JobSearchSerializer(serializers.Serializer):
    """
    Serializer for job search requests
    """

    query = serializers.CharField(
        max_length=500, required=False, help_text="Search query for title, description, company, location"
    )
    location = serializers.CharField(max_length=255, required=False, help_text="Filter by location")
    company = serializers.CharField(max_length=255, required=False, help_text="Filter by company name")
    category = serializers.CharField(max_length=255, required=False, help_text="Filter by category name")
    salary_min = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, help_text="Minimum salary")
    salary_max = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, help_text="Maximum salary")
    date_posted = serializers.ChoiceField(
        choices=[("today", "Today"), ("week", "This Week"), ("month", "This Month"), ("all", "All Time")],
        required=False,
        help_text="Filter by posting date",
    )
    sort_by = serializers.ChoiceField(
        choices=[
            ("relevance", "Relevance"),
            ("date_posted", "Date Posted"),
            ("salary", "Salary"),
            ("company", "Company Name"),
            ("title", "Job Title"),
        ],
        default="relevance",
        help_text="Sort results by",
    )
    sort_order = serializers.ChoiceField(
        choices=[("asc", "Ascending"), ("desc", "Descending")], default="desc", help_text="Sort order"
    )
    page = serializers.IntegerField(min_value=1, default=1, help_text="Page number")
    page_size = serializers.IntegerField(min_value=1, max_value=100, default=20, help_text="Results per page")
    promoted_only = serializers.BooleanField(default=False, help_text="Show only promoted jobs")
    remote_only = serializers.BooleanField(default=False, help_text="Show only remote jobs")


# Search response serializer
class JobSearchResponseSerializer(serializers.Serializer):
    """
    Serializer for job search responses
    """

    results = JobSerializer(many=True)
    total_count = serializers.IntegerField()
    page = serializers.IntegerField()
    page_size = serializers.IntegerField()
    total_pages = serializers.IntegerField()
    has_next = serializers.BooleanField()
    has_previous = serializers.BooleanField()
    search_time = serializers.FloatField(help_text="Search execution time in seconds")
    search_query = serializers.CharField(help_text="The search query used")
    filters_applied = serializers.DictField(help_text="Filters that were applied")
