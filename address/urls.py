"""
URL configuration for the address app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AddressViewSet, CityViewSet, StateViewSet, CountryViewSet
from .lookup_views import (
    get_countries,
    get_states_by_country,
    get_cities_by_state,
    search_locations,
    validate_address,
    get_address_hierarchy,
    get_address_statistics,
)

router = DefaultRouter()
router.register(r'addresses', AddressViewSet, basename='address')
# router.register(r'cities', CityViewSet, basename='city')
# router.register(r'states', StateViewSet, basename='state')
# router.register(r'countries', CountryViewSet, basename='country')

urlpatterns = [
    # Lookup endpoints
    path('lookup/countries/', get_countries, name='address-lookup-countries'),
    path('lookup/states/', get_states_by_country, name='address-lookup-states'),
    path('lookup/cities/', get_cities_by_state, name='address-lookup-cities'),
    path('lookup/search/', search_locations, name='address-search-locations'),
    path('lookup/hierarchy/', get_address_hierarchy, name='address-hierarchy'),

    path('validate/', validate_address, name='address-validate'),
    path('statistics/', get_address_statistics, name='address-statistics'),

    
    # CRUD endpoints
    path('', include(router.urls)),
]