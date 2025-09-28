from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Company
from .serializers import CompanySerializer, CompanyCreateSerializer
from rest_framework.permissions import IsAuthenticated
from core.pagination import DefaultPagination
from drf_spectacular.utils import extend_schema
from core.response import APIResponse
from core.permissions_enhanced import IsCompanyOwnerOrStaff, IsRecruiterOrAdmin
from core.viewset_permissions import get_company_permissions, get_company_queryset



class CompanyViewSet(viewsets.ModelViewSet):
    """
    Viewset for the company model
    """
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    
    def get_permissions(self):
        return get_company_permissions(self)
        

    def get_queryset(self):
        """
        Get the queryset for the company list
        """
        # if self.request.user.is_staff:
        #     return self.queryset
        # else:
        #     return self.queryset.filter(user=self.request.user)
        return get_company_queryset(self)

    
    @extend_schema(
        summary="Create company",
        description="Create a new company",
        responses={201: CompanySerializer},
        request=CompanyCreateSerializer,
    )
    def create(self, request, *args, **kwargs):
        """
        Create a company
        """
        serializer = CompanyCreateSerializer(data=request.data)
        if serializer.is_valid():
            # Set the user to the current authenticated user
            company = serializer.save(user=request.user)
            response_serializer = CompanySerializer(company)
            # return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            return APIResponse.created(
                response_serializer.data,
                message="Company created successfully"
            )
        return APIResponse.error(
            message="Company creation failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )