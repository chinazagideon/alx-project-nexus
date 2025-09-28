from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Address, City, State, Country
from .serializers import (
    AddressSerializer,
    AddressCreateSerializer,
    AddressNestedSerializer,
    CitySerializer,
    StateSerializer,
    CountrySerializer,
    CountryLookupSerializer,
    StateLookupSerializer,
    CityLookupSerializer,
    AddressValidationSerializer,
    AddressSearchSerializer,
)
from .services import AddressService, AddressLookupService
from .mixins import AddressLookupMixin
from core.pagination import DefaultPagination
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from core.permissions_enhanced import IsAddressOwnerOrStaff, IsAdminOnly
from core.viewset_permissions import get_address_permissions, get_address_queryset, get_city_state_country_permissions


class AddressViewSet(viewsets.ModelViewSet):
    """
    Viewset for the address model
    """

    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    pagination_class = DefaultPagination

    def get_permissions(self):
        return get_address_permissions(self)

    def get_queryset(self):
        """
        Get the queryset for the address list
        """
        return get_address_queryset(self)


class CityViewSet(viewsets.ModelViewSet):
    """
    Viewset for the city model
    """

    queryset = City.objects.all()
    serializer_class = CitySerializer

    def get_permissions(self):
        return get_city_state_country_permissions(self)

    def get_queryset(self):
        """
        Get the queryset for the city list
        """
        return super().get_queryset()

    @extend_schema(exclude=False)
    def destroy(self, request, *args, **kwargs):
        """
        Hide the DELETE endpoint from docs
        """
        return super().destroy(request, *args, **kwargs)

    @extend_schema(exclude=False)
    def update(self, request, *args, **kwargs):
        """
        Hide the PUT endpoint from docs
        """
        return super().update(request, *args, **kwargs)

    @extend_schema(exclude=False)
    def partial_update(self, request, *args, **kwargs):
        """
        Hide the PATCH endpoint from docs
        """
        return super().partial_update(request, *args, **kwargs)

    # hide the endpoints from docs
    @extend_schema(exclude=False)
    def create(self, request, *args, **kwargs):
        """
        Hide the POST endpoint from docs
        """
        return super().create(request, *args, **kwargs)


class StateViewSet(viewsets.ModelViewSet):
    """
    Viewset for the state model
    """

    queryset = State.objects.all()
    serializer_class = StateSerializer
    pagination_class = DefaultPagination

    def get_permissions(self):
        """
        Permission method for StateViewSet
        """
        return get_city_state_country_permissions(self)

    def get_queryset(self):
        """
        Get the queryset for the state list
        """
        return super().get_queryset()

    @extend_schema(exclude=False)
    def destroy(self, request, *args, **kwargs):
        """
        Hide the DELETE endpoint from docs
        """
        return super().destroy(request, *args, **kwargs)

    @extend_schema(exclude=False)
    def update(self, request, *args, **kwargs):
        """
        Hide the PUT endpoint from docs
        """
        return super().update(request, *args, **kwargs)

    @extend_schema(exclude=False)
    def partial_update(self, request, *args, **kwargs):
        """
        Hide the PATCH endpoint from docs
        """
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(exclude=False)
    def create(self, request, *args, **kwargs):
        """
        Hide the POST endpoint from docs
        """
        return super().create(request, *args, **kwargs)


class CountryViewSet(viewsets.ModelViewSet):
    """
    Viewset for the country model
    """

    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    pagination_class = DefaultPagination

    def get_permissions(self):
        """
        Permission method for CountryViewSet
        """
        return get_city_state_country_permissions(self)

    def get_queryset(self):
        """
        Get the queryset for the country list
        """
        return super().get_queryset()

    @extend_schema(exclude=False)
    def destroy(self, request, *args, **kwargs):
        """
        Hide the DELETE endpoint from docs
        """
        return super().destroy(request, *args, **kwargs)

    @extend_schema(exclude=False)
    def update(self, request, *args, **kwargs):
        """
        Hide the PUT endpoint from docs
        """
        return super().update(request, *args, **kwargs)

    @extend_schema(exclude=False)
    def partial_update(self, request, *args, **kwargs):
        """
        Hide the PATCH endpoint from docs
        """
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(exclude=False)
    def create(self, request, *args, **kwargs):
        """
        Hide the POST endpoint from docs
        """
        return super().create(request, *args, **kwargs)
