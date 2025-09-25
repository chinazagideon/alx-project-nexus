"""
Serializers for the jobs app
"""
from rest_framework import serializers
from django.db.models import Q, F, Case, When, Value, CharField
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from drf_spectacular.utils import extend_schema_field
from .models import Job, Category, JobCategory

# Job serializer
class JobSerializer(serializers.ModelSerializer):
    """
    Serializer for the job listing model
    """
    company_name = serializers.CharField(source='company.name', read_only=True)
    company_description = serializers.CharField(source='company.description', read_only=True)
    city_name = serializers.CharField(source='city.name', read_only=True)
    # address_city = serializers.CharField(source='address.city', read_only=True)
    # address_state = serializers.CharField(source='address.state', read_only=True)
    # address_country = serializers.CharField(source='address.country', read_only=True)
    categories = serializers.SerializerMethodField()
    is_promoted = serializers.BooleanField(read_only=True)
    promotion_priority = serializers.IntegerField(read_only=True)
    
    class Meta:
        """
        Meta class for the job serializer
        """
        model = Job
        fields = (
            'id',
            'title',
            'description',
            'company',
            'company_name',
            'company_description',
            'physical_address',
            'city',
            'city_name',
            'salary_min',
            'salary_max',
            'date_posted',
            'close_date',
            'updated_at',
            'categories',
            'is_promoted',
            'promotion_priority',
        )
        read_only_fields = ('date_posted', 'close_date')
    
    @extend_schema_field(serializers.ListField(child=serializers.CharField()))
    def get_categories(self, obj):
        """Get job categories"""
        return [cat.category.name for cat in obj.jobcategory_set.all()]

# Search request serializer
class JobSearchSerializer(serializers.Serializer):
    """
    Serializer for job search requests
    """
    query = serializers.CharField(max_length=500, required=False, help_text="Search query for title, description, company, location")
    location = serializers.CharField(max_length=255, required=False, help_text="Filter by location")
    company = serializers.CharField(max_length=255, required=False, help_text="Filter by company name")
    category = serializers.CharField(max_length=255, required=False, help_text="Filter by category name")
    salary_min = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, help_text="Minimum salary")
    salary_max = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, help_text="Maximum salary")
    date_posted = serializers.ChoiceField(
        choices=[
            ('today', 'Today'),
            ('week', 'This Week'),
            ('month', 'This Month'),
            ('all', 'All Time')
        ],
        required=False,
        help_text="Filter by posting date"
    )
    sort_by = serializers.ChoiceField(
        choices=[
            ('relevance', 'Relevance'),
            ('date_posted', 'Date Posted'),
            ('salary', 'Salary'),
            ('company', 'Company Name'),
            ('title', 'Job Title')
        ],
        default='relevance',
        help_text="Sort results by"
    )
    sort_order = serializers.ChoiceField(
        choices=[('asc', 'Ascending'), ('desc', 'Descending')],
        default='desc',
        help_text="Sort order"
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