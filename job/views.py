"""
Views for the jobs app
"""
from django.shortcuts import render
from .models import Job
from job.serializers import JobSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend


class JobListCreateView(generics.ListCreateAPIView):
    """
    View for listing and creating jobs
    """
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['title', 'company', 'address', 'location']
    search_fields = ['title', 'description', 'company__name', 'address__city', 'address__state', 'address__country']
    ordering_fields = ['created_at', 'updated_at']

class JobDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View for retrieving, updating and deleting jobs
    """
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]