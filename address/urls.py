"""
URL configuration for the address app
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .lookup_views import (
    get_address_hierarchy,
    get_address_statistics,
    get_cities_by_state,
    get_countries,
    get_states_by_country,
    search_locations,
    validate_address,
)
from .views import AddressViewSet, CityViewSet, CountryViewSet, StateViewSet

router = DefaultRouter()
router.register(r"", AddressViewSet, basename="address")
# router.register(r'cities', CityViewSet, basename='city')
# router.register(r'states', StateViewSet, basename='state')
# router.register(r'countries', CountryViewSet, basename='country')

urlpatterns = [
    # Lookup endpoints
    path("lookup/countries/", get_countries, name="address-lookup-countries"),
    path("lookup/states/", get_states_by_country, name="address-lookup-states"),
    path("lookup/cities/", get_cities_by_state, name="address-lookup-cities"),
    path("lookup/search/", search_locations, name="address-search-locations"),
    path("lookup/hierarchy/", get_address_hierarchy, name="address-hierarchy"),
    path("validate/", validate_address, name="address-validate"),
    path("statistics/", get_address_statistics, name="address-statistics"),
    # CRUD endpoints
    path("", include(router.urls)),
]
