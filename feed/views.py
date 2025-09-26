from typing import Optional

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db.models import Prefetch
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

from .models import FeedItem
from .serializers import FeedItemSerializer, FeedListResponseSerializer
from .services import zpage_by_cursor


@method_decorator(cache_page(5), name='dispatch')
class FeedListView(APIView):
    """
    Viewset for the feed list
    """
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Get global feed",
        parameters=[
            OpenApiParameter(
                name="limit", 
                required=False, 
                type=int, 
                description="Page size (default 20)",
                examples=[
                    OpenApiExample("Default", value=20),
                    OpenApiExample("Medium", value=50),
                    OpenApiExample("Large", value=100)
                ]
            ),
            OpenApiParameter(
                name="cursor", 
                required=False, 
                type=str, 
                description="Pagination cursor",
                examples=[
                    OpenApiExample("Example 1", value="eyJpZCI6MTIzfQ=="),
                    OpenApiExample("Example 2", value="eyJpZCI6NDU2fQ==")
                ]
            ),
            OpenApiParameter(
                name="types", 
                required=False, 
                type=str, 
                description="Comma list: job_posted,company_joined,promotion_active",
                examples=[
                    OpenApiExample("Single type", value="job_posted"),
                    OpenApiExample("Multiple types", value="job_posted,company_joined"),
                    OpenApiExample("All types", value="job_posted,company_joined,promotion_active")
                ]
            ),
        ],
        responses={200: FeedListResponseSerializer},
    )
    def get(self, request):
        """
        Get the feed list
        """
        limit = int(request.query_params.get("limit", 20))
        limit = max(1, min(limit, 100))
        cursor: Optional[str] = request.query_params.get("cursor")
        types_filter = request.query_params.get("types")
        allowed_types = None
        if types_filter:
            allowed_types = set(t.strip() for t in types_filter.split(",") if t.strip())

        ids, next_cursor = zpage_by_cursor(limit=limit, cursor=cursor)

        # Fallback: if Redis empty, query DB directly
        if not ids:
            queryset = FeedItem.objects.filter(is_active=True)
            if allowed_types:
                queryset = queryset.filter(event_type__in=allowed_types)
            queryset = queryset.order_by("-score", "-id")[:limit]
            items = list(queryset)
        else:
            items_map = {fi.id: fi for fi in FeedItem.objects.filter(id__in=ids)}
            items = [items_map[i] for i in ids if i in items_map]
            if allowed_types:
                items = [i for i in items if i.event_type in allowed_types]

        serializer = FeedItemSerializer(items, many=True)
        return Response({
            "results": serializer.data,
            "next_cursor": next_cursor,
        }, status=status.HTTP_200_OK)


