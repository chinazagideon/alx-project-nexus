"""
Views for the jobs app
"""
from .models import Job
from .serializers import JobSerializer, JobSearchSerializer, JobSearchResponseSerializer
from .search_service import JobSearchService
from rest_framework import generics, viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from rest_framework.pagination import PageNumberPagination
from django.contrib.contenttypes.models import ContentType
from django.db.models import Exists, OuterRef, Subquery, Value, IntegerField
from django.db.models.functions import Coalesce
from promotion.models import Promotion



class JobListCreateView(generics.ListCreateAPIView):
    """
    View for listing and creating jobs
    """
    queryset = Job.objects.all()
    serializer_class = JobSerializer

    permission_classes = [IsAuthenticated]

    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['title', 'company', 'address', 'location']
    search_fields = ['title', 'description', 'company__name', 'address__city', 'address__state', 'address__country']
    ordering_fields = ['date_posted', 'updated_at']

    def get_queryset(self):
        """
        Get the queryset for the job list
        """
        base_qs = super().get_queryset()
        job_ct = ContentType.objects.get_for_model(Job)
        active_promotions = Promotion.objects.active().filter(content_type=job_ct, object_id=OuterRef('pk'))

        priority_subquery = Subquery(
            active_promotions.values('package__priority_weight')[:1],
            output_field=IntegerField(),
        )

        annotated = base_qs.annotate(
            is_promoted=Exists(active_promotions),
            promotion_priority=Coalesce(priority_subquery, Value(0)),
        )

        return annotated.order_by('-is_promoted', '-promotion_priority', '-date_posted')

class JobViewSet(viewsets.ModelViewSet):
    """
    View for listing and creating jobs
    """
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Get the queryset for the job list
        """
        return super().get_queryset()


# Search API endpoints
@extend_schema(
    operation_id='job_search',
    summary='Advanced Job Search',
    description='Search jobs with advanced filtering, sorting, and pagination options',
    request=JobSearchSerializer,
    responses={
        200: JobSearchResponseSerializer,
        400: OpenApiTypes.OBJECT,
    },
    parameters=[
        OpenApiParameter(
            name='query',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Search query for title, description, company, location',
            examples=[
                OpenApiExample('Basic search', value='python developer'),
                OpenApiExample('Location search', value='remote python developer'),
            ]
        ),
        OpenApiParameter(
            name='location',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Filter by location',
            examples=[OpenApiExample('Location filter', value='San Francisco')]
        ),
        OpenApiParameter(
            name='company',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Filter by company name',
            examples=[OpenApiExample('Company filter', value='Google')]
        ),
        OpenApiParameter(
            name='sort_by',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Sort results by',
            enum=['relevance', 'date_posted', 'salary', 'company', 'title'],
            default='relevance'
        ),
        OpenApiParameter(
            name='page',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='Page number',
            default=1
        ),
        OpenApiParameter(
            name='page_size',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='Results per page (max 100)',
            default=20
        ),
    ],
    examples=[
        OpenApiExample(
            'Basic GET Search',
            value={
                'query': 'python developer',
                'location': 'remote',
                'sort_by': 'relevance',
                'page': 1,
                'page_size': 20
            },
            request_only=True,
        ),
        OpenApiExample(
            'Advanced POST Search',
            value={
                'query': 'senior python developer',
                'location': 'San Francisco',
                'company': 'Google',
                'category': 'Software Engineering',
                'salary_min': 100000,
                'salary_max': 200000,
                'date_posted': 'month',
                'sort_by': 'relevance',
                'sort_order': 'desc',
                'promoted_only': False,
                'remote_only': True,
                'page': 1,
                'page_size': 20
            },
            request_only=True,
        ),
    ],
    tags=['Job Search']
)
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def job_search(request):
    """
    Advanced job search endpoint with comprehensive filtering and sorting options.
    
    Supports both GET (query parameters) and POST (request body) methods.
    Returns paginated results with search metadata.
    """
    search_service = JobSearchService()
    
    # Get search parameters
    if request.method == 'GET':
        search_data = request.query_params.dict()
    else:  # POST
        search_data = request.data
    
    try:
        # Perform search
        results = search_service.search(search_data)
        
        # Serialize response
        serializer = JobSearchResponseSerializer(results)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': str(e), 'message': 'Search failed'},
            status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema(
    operation_id='search_suggestions',
    summary='Get Search Suggestions',
    description='Get auto-complete suggestions based on partial query input',
    parameters=[
        OpenApiParameter(
            name='q',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Partial search query (minimum 2 characters)',
            required=True,
            examples=[
                OpenApiExample('Job title', value='python'),
                OpenApiExample('Company', value='goog'),
                OpenApiExample('Location', value='san'),
            ]
        ),
        OpenApiParameter(
            name='limit',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='Maximum number of suggestions to return',
            default=10
        ),
    ],
    responses={
        200: {
            'type': 'object',
            'properties': {
                'suggestions': {
                    'type': 'array',
                    'items': {'type': 'string'},
                    'description': 'List of search suggestions'
                }
            },
            'example': {
                'suggestions': [
                    'Python Developer',
                    'Python Engineer', 
                    'Senior Python Developer',
                    'Python Backend Developer',
                    'Google',
                    'San Francisco'
                ]
            }
        }
    },
    tags=['Job Search']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def search_suggestions(request):
    """
    Get auto-complete search suggestions based on partial query input.
    
    Returns suggestions from job titles, company names, and locations.
    """
    query = request.query_params.get('q', '')
    limit = int(request.query_params.get('limit', 10))
    
    if len(query) < 2:
        return Response({'suggestions': []})
    
    search_service = JobSearchService()
    suggestions = search_service.get_search_suggestions(query, limit)
    
    return Response({'suggestions': suggestions})


@extend_schema(
    operation_id='search_facets',
    summary='Get Search Facets',
    description='Get available filter options and their counts for search refinement',
    responses={
        200: {
            'type': 'object',
            'properties': {
                'locations': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'name': {'type': 'string'},
                            'count': {'type': 'integer'}
                        }
                    }
                },
                'companies': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'name': {'type': 'string'},
                            'count': {'type': 'integer'}
                        }
                    }
                },
                'categories': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'name': {'type': 'string'},
                            'count': {'type': 'integer'}
                        }
                    }
                },
                'salary_ranges': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'range': {'type': 'string'},
                            'count': {'type': 'integer'}
                        }
                    }
                }
            },
            'example': {
                'locations': [
                    {'name': 'San Francisco', 'count': 125},
                    {'name': 'New York', 'count': 98},
                    {'name': 'Remote', 'count': 87}
                ],
                'companies': [
                    {'name': 'Google', 'count': 45},
                    {'name': 'Apple', 'count': 32}
                ],
                'categories': [
                    {'name': 'Software Engineering', 'count': 156},
                    {'name': 'Data Science', 'count': 89}
                ],
                'salary_ranges': [
                    {'range': '$100k-$150k', 'count': 78},
                    {'range': '$150k+', 'count': 45}
                ]
            }
        }
    },
    tags=['Job Search']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def search_facets(request):
    """
    Get available filter options and their counts for search refinement.
    
    Returns faceted search data to help users understand available filtering options.
    """
    search_service = JobSearchService()
    
    # Get base queryset with current filters
    base_queryset = search_service._build_base_queryset()
    
    # Apply any existing filters from query params
    search_data = request.query_params.dict()
    if search_data:
        validated_data = JobSearchSerializer(data=search_data)
        if validated_data.is_valid():
            base_queryset = search_service._apply_filters(base_queryset, validated_data.validated_data)
    
    facets = search_service.get_facet_counts(base_queryset)
    
    return Response(facets)


@extend_schema(
    operation_id='job_stats',
    summary='Get Job Statistics',
    description='Get overall job portal statistics and metrics',
    responses={
        200: {
            'type': 'object',
            'properties': {
                'total_jobs': {
                    'type': 'integer',
                    'description': 'Total number of jobs in the system'
                },
                'jobs_today': {
                    'type': 'integer',
                    'description': 'Jobs posted today'
                },
                'jobs_this_week': {
                    'type': 'integer',
                    'description': 'Jobs posted in the last 7 days'
                },
                'jobs_this_month': {
                    'type': 'integer',
                    'description': 'Jobs posted in the last 30 days'
                },
                'companies_count': {
                    'type': 'integer',
                    'description': 'Number of unique companies'
                },
                'locations_count': {
                    'type': 'integer',
                    'description': 'Number of unique job locations'
                }
            },
            'example': {
                'total_jobs': 1250,
                'jobs_today': 15,
                'jobs_this_week': 87,
                'jobs_this_month': 342,
                'companies_count': 156,
                'locations_count': 89
            }
        }
    },
    tags=['Job Search']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def job_stats(request):
    """
    Get overall job portal statistics and metrics.
    
    Returns key metrics about jobs, companies, and locations in the system.
    """
    from django.db.models import Count
    from django.utils import timezone
    from datetime import timedelta
    
    now = timezone.now()
    
    stats = {
        'total_jobs': Job.objects.count(),
        'jobs_today': Job.objects.filter(date_posted__date=now.date()).count(),
        'jobs_this_week': Job.objects.filter(
            date_posted__gte=now - timedelta(days=7)
        ).count(),
        'jobs_this_month': Job.objects.filter(
            date_posted__gte=now - timedelta(days=30)
        ).count(),
        'companies_count': Job.objects.values('company').distinct().count(),
        'locations_count': Job.objects.values('location').distinct().count(),
    }
    
    return Response(stats)
