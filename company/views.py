from django.shortcuts import render
from rest_framework import viewsets
from .models import Company
from .serializers import CompanySerializer
from rest_framework.permissions import IsAuthenticated
from core.pagination import DefaultPagination
from drf_spectacular.utils import extend_schema


class CompanyViewSet(viewsets.ModelViewSet):
    """
    Viewset for the company model
    """
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPagination

    def get_queryset(self):
        """
        Get the queryset for the company list
        """

        return super().get_queryset()
    
    @extend_schema(
        summary="Create company",
        description="Create a new company",
        responses={200: CompanySerializer},
        request=CompanySerializer,
    )
    def create(self, request, *args, **kwargs):
        """
        Create a company
        """
        pass