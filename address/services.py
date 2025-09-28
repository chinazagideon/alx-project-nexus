"""
Address services for lookup, validation, and management
"""

from typing import Dict, List, Optional, Tuple
from django.db.models import Q
from django.core.cache import cache
from .models import Address, City, State, Country


class AddressService:
    """
    Service class for address operations
    """

    def __init__(self):
        self.cache_timeout = 300  # 5 minutes

    def get_or_create_address(self, address_data: Dict) -> Tuple[Address, bool]:
        """
        Get existing address or create new one

        Args:
            address_data: Dictionary containing address information

        Returns:
            Tuple of (Address instance, created boolean)
        """
        city_id = address_data.get("city_id")
        location = address_data.get("location")
        zip_code = address_data.get("zip_code")

        if not all([city_id, location, zip_code]):
            raise ValueError("Missing required address fields")

        # Try to find existing address
        try:
            address = Address.objects.get(city_id=city_id, location=location, zip_code=zip_code)
            return address, False
        except Address.DoesNotExist:
            # Create new address
            address = Address.objects.create(city_id=city_id, location=location, zip_code=zip_code)
            return address, True

    def validate_address(self, address_data: Dict) -> Dict:
        """
        Validate address data and return validation result

        Args:
            address_data: Dictionary containing address information

        Returns:
            Dictionary with validation result and suggestions
        """
        result = {"is_valid": True, "errors": [], "suggestions": [], "normalized_address": None}

        # Validate required fields
        required_fields = ["location", "city_id", "zip_code"]
        for field in required_fields:
            if not address_data.get(field):
                result["errors"].append(f"Missing required field: {field}")
                result["is_valid"] = False

        if not result["is_valid"]:
            return result

        # Validate city exists
        try:
            city = City.objects.select_related("state__country").get(id=address_data["city_id"])
            result["normalized_address"] = {
                "location": address_data["location"].strip(),
                "city": city.name,
                "state": city.state.name,
                "country": city.state.country.name,
                "zip_code": address_data["zip_code"].strip(),
            }
        except City.DoesNotExist:
            result["errors"].append("Invalid city ID")
            result["is_valid"] = False

        return result

    def search_addresses(self, query: str, filters: Dict = None) -> List[Address]:
        """
        Search addresses based on query and filters

        Args:
            query: Search query string
            filters: Additional filters (country_id, state_id, city_id)

        Returns:
            List of matching addresses
        """
        queryset = Address.objects.select_related("city__state__country").filter(status=True)

        # Apply text search
        if query:
            queryset = queryset.filter(
                Q(location__icontains=query)
                | Q(city__name__icontains=query)
                | Q(city__state__name__icontains=query)
                | Q(city__state__country__name__icontains=query)
                | Q(zip_code__icontains=query)
            )

        # Apply filters
        if filters:
            if filters.get("country_id"):
                queryset = queryset.filter(city__state__country_id=filters["country_id"])
            if filters.get("state_id"):
                queryset = queryset.filter(city__state_id=filters["state_id"])
            if filters.get("city_id"):
                queryset = queryset.filter(city_id=filters["city_id"])

        return queryset.distinct()

    def get_address_hierarchy(self, country_id: int = None, state_id: int = None) -> Dict:
        """
        Get address hierarchy for cascading dropdowns

        Args:
            country_id: Optional country ID to filter states
            state_id: Optional state ID to filter cities

        Returns:
            Dictionary with countries, states, and cities
        """
        cache_key = f"address_hierarchy_{country_id}_{state_id}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result

        result = {"countries": [], "states": [], "cities": []}

        # Get countries
        countries = Country.objects.all().order_by("name")
        result["countries"] = [{"id": c.id, "name": c.name, "code": c.code} for c in countries]

        # Get states (filtered by country if provided)
        states_query = State.objects.select_related("country")
        if country_id:
            states_query = states_query.filter(country_id=country_id)

        states = states_query.order_by("name")
        result["states"] = [{"id": s.id, "name": s.name, "country_id": s.country_id} for s in states]

        # Get cities (filtered by state if provided)
        cities_query = City.objects.select_related("state__country")
        if state_id:
            cities_query = cities_query.filter(state_id=state_id)
        elif country_id:
            cities_query = cities_query.filter(state__country_id=country_id)

        cities = cities_query.order_by("name")
        result["cities"] = [{"id": c.id, "name": c.name, "state_id": c.state_id} for c in cities]

        cache.set(cache_key, result, self.cache_timeout)
        return result

    def get_location_suggestions(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Get location suggestions for autocomplete

        Args:
            query: Search query
            limit: Maximum number of suggestions

        Returns:
            List of location suggestions
        """
        if len(query) < 2:
            return []

        cache_key = f"location_suggestions_{query}_{limit}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result

        suggestions = []

        # Search cities
        cities = City.objects.select_related("state__country").filter(name__icontains=query)[: limit // 2]

        for city in cities:
            suggestions.append(
                {
                    "type": "city",
                    "id": city.id,
                    "name": city.name,
                    "state": city.state.name,
                    "country": city.state.country.name,
                    "display": f"{city.name}, {city.state.name}, {city.state.country.name}",
                }
            )

        # Search states
        states = State.objects.select_related("country").filter(name__icontains=query)[: limit // 4]

        for state in states:
            suggestions.append(
                {
                    "type": "state",
                    "id": state.id,
                    "name": state.name,
                    "country": state.country.name,
                    "display": f"{state.name}, {state.country.name}",
                }
            )

        # Search countries
        countries = Country.objects.filter(name__icontains=query)[: limit // 4]

        for country in countries:
            suggestions.append({"type": "country", "id": country.id, "name": country.name, "display": country.name})

        cache.set(cache_key, suggestions, self.cache_timeout)
        return suggestions[:limit]

    def normalize_address(self, address_data: Dict) -> Dict:
        """
        Normalize address data for consistency

        Args:
            address_data: Raw address data

        Returns:
            Normalized address data
        """
        normalized = {
            "location": address_data.get("location", "").strip().title(),
            "zip_code": address_data.get("zip_code", "").strip().upper(),
            "city_id": address_data.get("city_id"),
        }

        # Get city information for additional normalization
        if normalized["city_id"]:
            try:
                city = City.objects.select_related("state__country").get(id=normalized["city_id"])
                normalized.update(
                    {
                        "city_name": city.name,
                        "state_name": city.state.name,
                        "country_name": city.state.country.name,
                        "country_code": city.state.country.code,
                    }
                )
            except City.DoesNotExist:
                pass

        return normalized

    def get_address_statistics(self) -> Dict:
        """
        Get address-related statistics

        Returns:
            Dictionary with address statistics
        """
        cache_key = "address_statistics"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result

        stats = {
            "total_addresses": Address.objects.filter(status=True).count(),
            "total_cities": City.objects.count(),
            "total_states": State.objects.count(),
            "total_countries": Country.objects.count(),
            "countries_with_addresses": Address.objects.filter(status=True)
            .values_list("city__state__country__name", flat=True)
            .distinct()
            .count(),
        }

        cache.set(cache_key, stats, self.cache_timeout)
        return stats


class AddressLookupService:
    """
    Service for address lookup operations
    """

    @staticmethod
    def get_countries() -> List[Dict]:
        """Get all countries"""
        return list(Country.objects.values("id", "name", "code").order_by("name"))

    @staticmethod
    def get_states_by_country(country_id: int) -> List[Dict]:
        """Get states by country ID"""
        return list(State.objects.filter(country_id=country_id).values("id", "name", "country_id").order_by("name"))

    @staticmethod
    def get_cities_by_state(state_id: int) -> List[Dict]:
        """Get cities by state ID"""
        return list(City.objects.filter(state_id=state_id).values("id", "name", "state_id").order_by("name"))

    @staticmethod
    def get_cities_by_country(country_id: int) -> List[Dict]:
        """Get cities by country ID"""
        return list(
            City.objects.filter(state__country_id=country_id)
            .select_related("state")
            .values("id", "name", "state_id", "state__name")
            .order_by("name")
        )

    @staticmethod
    def search_locations(query: str, limit: int = 20) -> List[Dict]:
        """Search across all location types"""
        if len(query) < 2:
            return []

        results = []

        # Search cities
        cities = City.objects.select_related("state__country").filter(name__icontains=query)[: limit // 2]

        for city in cities:
            results.append(
                {
                    "type": "city",
                    "id": city.id,
                    "name": city.name,
                    "parent": f"{city.state.name}, {city.state.country.name}",
                    "full_name": f"{city.name}, {city.state.name}, {city.state.country.name}",
                }
            )

        # Search states
        states = State.objects.select_related("country").filter(name__icontains=query)[: limit // 4]

        for state in states:
            results.append(
                {
                    "type": "state",
                    "id": state.id,
                    "name": state.name,
                    "parent": state.country.name,
                    "full_name": f"{state.name}, {state.country.name}",
                }
            )

        # Search countries
        countries = Country.objects.filter(name__icontains=query)[: limit // 4]

        for country in countries:
            results.append(
                {"type": "country", "id": country.id, "name": country.name, "parent": None, "full_name": country.name}
            )

        return results[:limit]
