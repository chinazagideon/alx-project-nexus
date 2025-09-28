"""
Advanced search service for jobs
"""

import hashlib
import re
import time
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Case, CharField, Exists, F, IntegerField, OuterRef, Q, Subquery, Value, When
from django.utils import timezone

from .models import Category, Job, JobCategory
from .serializers import JobSearchSerializer


class JobSearchService:
    """
    Advanced job search service with multiple search strategies
    """

    def __init__(self):
        self.search_weights = {
            "title": "A",  # Highest weight
            "description": "B",
            "company__name": "C",
            "location": "D",
            "categories__name": "C",
        }

    def search(self, search_data: Dict, user=None) -> Dict:
        """
        Main search method that orchestrates different search strategies
        """
        start_time = time.time()

        # Validate search data
        serializer = JobSearchSerializer(data=search_data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        # Check cache first (disabled for testing)
        # cache_key = self._get_cache_key(validated_data)
        # cached_result = cache.get(cache_key)
        # if cached_result:
        #     cached_result['search_time'] = time.time() - start_time
        #     return cached_result

        # Build base queryset
        queryset = self._build_base_queryset(user)

        # Apply text search
        if validated_data.get("query"):
            queryset = self._apply_text_search(queryset, validated_data["query"])

        # Apply filters
        queryset = self._apply_filters(queryset, validated_data)

        # Apply sorting
        queryset = self._apply_sorting(queryset, validated_data)

        # Apply pagination
        paginated_results = self._apply_pagination(queryset, validated_data)

        # Calculate search time
        search_time = time.time() - start_time

        # Build response
        result = self._build_response(paginated_results, validated_data, search_time)

        # Cache result for 5 minutes (disabled for testing)
        # cache.set(cache_key, result, 300)

        return result

    def _get_cache_key(self, validated_data: Dict) -> str:
        """
        Generate cache key for search results
        """
        # Create a hash of the search parameters
        search_str = str(sorted(validated_data.items()))
        return f"job_search:{hashlib.md5(search_str.encode()).hexdigest()}"

    def _build_base_queryset(self, user=None):
        """
        Build base queryset with promotions and related data
        """
        from django.contrib.contenttypes.models import ContentType

        from promotion.models import Promotion

        # Start with base queryset
        base_qs = Job.objects.select_related("company", "city").prefetch_related("jobcategory_set__category")

        # Apply permission filtering
        if user and not user.is_staff:
            if user.role == "recruiter":
                base_qs = base_qs.filter(company__user=user)
            # talent users can see all jobs (no additional filtering)

        job_ct = ContentType.objects.get_for_model(Job)
        active_promotions = Promotion.objects.active().filter(content_type=job_ct, object_id=OuterRef("id"))

        priority_subquery = active_promotions.values("package__priority_weight")[:1]

        return base_qs.annotate(
            is_promoted=Q(id__in=active_promotions.values("object_id")),
            promotion_priority=Case(
                When(is_promoted=True, then=priority_subquery), default=Value(0), output_field=IntegerField()
            ),
        )

    def _apply_text_search(self, queryset, query: str):
        """
        Apply full-text search using multiple strategies
        """
        # Strategy 1: PostgreSQL Full-Text Search (if available)
        if self._is_postgresql():
            return self._postgresql_search(queryset, query)

        # Strategy 2: Django ORM search
        return self._django_orm_search(queryset, query)

    def _is_postgresql(self) -> bool:
        """Check if using PostgreSQL"""
        from django.db import connection

        return connection.vendor == "postgresql"

    def _postgresql_search(self, queryset, query: str):
        """
        PostgreSQL full-text search with ranking
        """
        # Create search vector
        search_vector = SearchVector("title", "description", "company__name", "city__name")

        # Create search query
        search_query = SearchQuery(query)

        # Apply search with ranking
        return (
            queryset.annotate(search=search_vector, rank=SearchRank(search_vector, search_query))
            .filter(search=search_query)
            .order_by("-rank", "-is_promoted", "-promotion_priority")
        )

    def _django_orm_search(self, queryset, query: str):
        """
        Django ORM-based search with relevance scoring
        """
        # Split query into terms
        terms = self._extract_search_terms(query)

        # Build Q objects for different fields with weights
        q_objects = Q()

        for term in terms:
            # Title matches (highest weight)
            title_q = Q(title__icontains=term)

            # Description matches
            desc_q = Q(description__icontains=term)

            # Company name matches
            company_q = Q(company__name__icontains=term)

            # City matches
            city_q = Q(city__name__icontains=term)

            # Category matches
            category_q = Q(jobcategory_set__category__name__icontains=term)

            # Combine with OR
            term_q = title_q | desc_q | company_q | city_q | category_q
            q_objects |= term_q

        # Apply search and add relevance scoring
        return (
            queryset.filter(q_objects)
            .annotate(relevance_score=self._calculate_relevance_score(query))
            .order_by("-relevance_score", "-is_promoted", "-promotion_priority")
        )

    def _extract_search_terms(self, query: str) -> List[str]:
        """
        Extract meaningful search terms from query
        """
        # Remove special characters and split
        terms = re.findall(r"\b\w+\b", query.lower())

        # Remove common stop words
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        return [term for term in terms if term not in stop_words and len(term) > 2]

    def _calculate_relevance_score(self, query: str):
        """
        Calculate relevance score for Django ORM search
        """
        terms = self._extract_search_terms(query)

        score = Case(
            # Title matches get highest score
            When(title__icontains=query, then=Value(100)),
            # Partial title matches
            *[When(title__icontains=term, then=Value(50)) for term in terms],
            # Description matches
            When(description__icontains=query, then=Value(30)),
            # Company matches
            When(company__name__icontains=query, then=Value(25)),
            # City matches
            When(city__name__icontains=query, then=Value(20)),
            # Category matches
            When(jobcategory_set__category__name__icontains=query, then=Value(15)),
            default=Value(0),
            output_field=IntegerField(),
        )

        return score

    def _apply_filters(self, queryset, validated_data: Dict):
        """
        Apply various filters to the queryset
        """
        # Location filter
        if validated_data.get("location"):
            location = validated_data["location"]
            queryset = queryset.filter(Q(city__name__icontains=location) | Q(physical_address__icontains=location))

        # Company filter
        if validated_data.get("company"):
            queryset = queryset.filter(company__name__icontains=validated_data["company"])

        # Category filter
        if validated_data.get("category"):
            queryset = queryset.filter(jobcategory_set__category__name__icontains=validated_data["category"])

        # Salary range filter
        if validated_data.get("salary_min") or validated_data.get("salary_max"):
            queryset = self._apply_salary_filter(queryset, validated_data)

        # Date posted filter
        if validated_data.get("date_posted"):
            queryset = self._apply_date_filter(queryset, validated_data["date_posted"])

        # Remote jobs filter
        if validated_data.get("remote_only"):
            queryset = queryset.filter(
                Q(city__name__icontains="remote")
                | Q(physical_address__icontains="remote")
                | Q(physical_address__icontains="work from home")
                | Q(physical_address__icontains="wfh")
            )

        # Promoted jobs filter
        if validated_data.get("promoted_only"):
            queryset = queryset.filter(is_promoted=True)

        return queryset

    def _apply_salary_filter(self, queryset, validated_data: Dict):
        """
        Apply salary range filtering
        """
        salary_min = validated_data.get("salary_min")
        salary_max = validated_data.get("salary_max")

        if salary_min:
            queryset = queryset.filter(salary_min__gte=salary_min)

        if salary_max:
            queryset = queryset.filter(salary_max__lte=salary_max)

        return queryset

    def _apply_date_filter(self, queryset, date_filter: str):
        """
        Apply date posted filtering
        """
        now = timezone.now()

        if date_filter == "today":
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif date_filter == "week":
            start_date = now - timedelta(days=7)
        elif date_filter == "month":
            start_date = now - timedelta(days=30)
        else:  # all
            return queryset

        return queryset.filter(date_posted__gte=start_date)

    def _apply_sorting(self, queryset, validated_data: Dict):
        """
        Apply sorting to the queryset
        """
        sort_by = validated_data.get("sort_by", "relevance")
        sort_order = validated_data.get("sort_order", "desc")

        # Determine sort field
        sort_fields = {
            "relevance": ["-is_promoted", "-promotion_priority", "-date_posted"],
            "date_posted": ["-date_posted"],
            "salary": ["salary_min", "salary_max"],
            "company": ["company__name"],
            "title": ["title"],
        }

        sort_field = sort_fields.get(sort_by, sort_fields["relevance"])

        # Apply sort order
        if sort_order == "asc":
            sort_field = [field.lstrip("-") if field.startswith("-") else f"-{field}" for field in sort_field]

        return queryset.order_by(*sort_field)

    def _apply_pagination(self, queryset, validated_data: Dict):
        """
        Apply pagination to the queryset
        """
        page = validated_data.get("page", 1)
        page_size = validated_data.get("page_size", 20)

        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)

        return {
            "results": page_obj.object_list,
            "total_count": paginator.count,
            "page": page_obj.number,
            "page_size": page_size,
            "total_pages": paginator.num_pages,
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous(),
        }

    def _build_response(self, paginated_results: Dict, validated_data: Dict, search_time: float) -> Dict:
        """
        Build the final search response
        """
        return {
            "results": paginated_results["results"],
            "total_count": paginated_results["total_count"],
            "page": paginated_results["page"],
            "page_size": paginated_results["page_size"],
            "total_pages": paginated_results["total_pages"],
            "has_next": paginated_results["has_next"],
            "has_previous": paginated_results["has_previous"],
            "search_time": round(search_time, 3),
            "search_query": validated_data.get("query", ""),
            "filters_applied": {
                k: v
                for k, v in validated_data.items()
                if v is not None and k not in ["page", "page_size", "sort_by", "sort_order"]
            },
        }

    def get_search_suggestions(self, query: str, limit: int = 10) -> List[str]:
        """
        Get search suggestions based on query
        """
        if len(query) < 2:
            return []

        suggestions = []

        # Job title suggestions
        title_suggestions = Job.objects.filter(title__icontains=query).values_list("title", flat=True).distinct()[: limit // 2]

        # Company name suggestions
        company_suggestions = (
            Job.objects.filter(company__name__icontains=query).values_list("company__name", flat=True).distinct()[: limit // 2]
        )

        # Location suggestions
        location_suggestions = (
            Job.objects.filter(Q(city__name__icontains=query) | Q(physical_address__icontains=query))
            .values_list("city__name", flat=True)
            .distinct()[: limit // 4]
        )

        suggestions.extend(title_suggestions)
        suggestions.extend(company_suggestions)
        suggestions.extend(location_suggestions)

        return list(set(suggestions))[:limit]

    def get_facet_counts(self, base_queryset) -> Dict:
        """
        Get facet counts for filters
        """
        # This would be implemented to provide counts for each filter option
        # For now, return empty dict
        return {"locations": [], "companies": [], "categories": [], "salary_ranges": []}

    def clear_search_cache(self):
        """
        Clear all search-related cache
        """
        # Clear all cache keys that start with 'job_search:'
        cache.delete_many(cache.keys("job_search:*"))

    def get_popular_searches(self, limit: int = 10) -> List[str]:
        """
        Get popular search terms (would need to be tracked in a separate model)
        """
        # This would typically come from a search analytics model
        # For now, return empty list
        return []

    def get_search_analytics(self) -> Dict:
        """
        Get search analytics data
        """
        # This would provide search analytics
        return {"total_searches": 0, "popular_queries": [], "search_performance": {}}
