"""
Address serializers
"""

from django.contrib.contenttypes.models import ContentType
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .models import Address, City, Country, State


# Base serializers for lookup and reference
class CountrySerializer(serializers.ModelSerializer):
    """
    Serializer for the country model
    """

    class Meta:
        model = Country
        fields = ("id", "name", "code")
        read_only_fields = ("id", "code")


class StateSerializer(serializers.ModelSerializer):
    """
    Serializer for the state model
    """

    country = CountrySerializer(read_only=True)
    country_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = State
        fields = ("id", "name", "country", "country_id")
        read_only_fields = ("id", "country")

    def validate_country_id(self, value):
        """Validate that country exists"""
        if not Country.objects.filter(id=value).exists():
            raise serializers.ValidationError("Country does not exist")
        return value


class CitySerializer(serializers.ModelSerializer):
    """
    Serializer for the city model
    """

    state = StateSerializer(read_only=True)
    state_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = City
        fields = ("id", "name", "state", "state_id")
        read_only_fields = ("id", "state")

    def validate_state_id(self, value):
        """Validate that state exists"""
        if not State.objects.filter(id=value).exists():
            raise serializers.ValidationError("State does not exist")
        return value


# Nested serializers for related entities
class AddressNestedSerializer(serializers.ModelSerializer):
    """
    Nested address serializer for use in other entities
    """

    city_name = serializers.CharField(source="city.name", read_only=True)
    state_name = serializers.CharField(source="city.state.name", read_only=True)
    country_name = serializers.CharField(source="city.state.country.name", read_only=True)
    country_code = serializers.CharField(source="city.state.country.code", read_only=True)

    class Meta:
        model = Address
        fields = (
            "id",
            "location",
            "city_name",
            "state_name",
            "country_name",
            "country_code",
            "zip_code",
        )
        read_only_fields = fields


class AddressCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating addresses with nested city/state/country
    """

    city_id = serializers.IntegerField(write_only=True)
    city_name = serializers.CharField(source="city.name", read_only=True)
    state_name = serializers.CharField(source="city.state.name", read_only=True)
    country_name = serializers.CharField(source="city.state.country.name", read_only=True)
    country_code = serializers.CharField(source="city.state.country.code", read_only=True)

    class Meta:
        model = Address
        fields = (
            "id",
            "location",
            "city_id",
            "city_name",
            "state_name",
            "country_name",
            "country_code",
            "zip_code",
        )
        read_only_fields = (
            "id",
            "city_name",
            "state_name",
            "country_name",
            "country_code",
        )

    def validate_city_id(self, value):
        """Validate that city exists"""
        if not City.objects.filter(id=value).exists():
            raise serializers.ValidationError("City does not exist")
        return value

    def validate(self, attrs):
        """Validate the complete address"""
        city_id = attrs.get("city_id")
        if city_id:
            city = City.objects.select_related("state__country").get(id=city_id)
            attrs["city"] = city
        return attrs


class AddressSerializer(serializers.ModelSerializer):
    """
    Full address serializer with nested relationships
    """

    city = CitySerializer(read_only=True)
    content_type = serializers.SlugRelatedField(slug_field="model", queryset=ContentType.objects.all())
    country_id = serializers.IntegerField(write_only=True, required=True)
    state_id = serializers.IntegerField(write_only=True, required=True)

    class Meta:
        model = Address
        fields = (
            "id",
            "location",
            "city",
            "country_id",
            "state_id",
            "content_type",
            "object_id",
            "zip_code",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at", "status")

    def validate_city_id(self, value):
        """Validate that city exists"""
        if not City.objects.filter(id=value).exists():
            raise serializers.ValidationError("City does not exist")
        return value

    #
    def validate(self, attrs):
        """Validate the complete address"""
        city_id = attrs.get("city_id")

        content_type = attrs.get("content_type")
        object_id = attrs.get("object_id")
        if city_id:
            city = City.objects.select_related("state__country").get(id=city_id)
            attrs["city"] = city
        return attrs


# Lookup serializers for dropdowns and autocomplete
class CountryLookupSerializer(serializers.ModelSerializer):
    """
    Simplified country serializer for lookups
    """

    class Meta:
        model = Country
        fields = ("id", "name", "code")


class StateLookupSerializer(serializers.ModelSerializer):
    """
    Simplified state serializer for lookups
    """

    country_name = serializers.CharField(source="country.name", read_only=True)

    class Meta:
        model = State
        fields = ("id", "name", "country_name")


class CityLookupSerializer(serializers.ModelSerializer):
    """
    Simplified city serializer for lookups
    """

    state_name = serializers.CharField(source="state.name", read_only=True)
    country_name = serializers.CharField(source="state.country.name", read_only=True)

    class Meta:
        model = City
        fields = ("id", "name", "state_name", "country_name")


# Address validation serializer
class AddressValidationSerializer(serializers.Serializer):
    """
    Serializer for validating address data
    """

    location = serializers.CharField(max_length=500)
    city_id = serializers.IntegerField()
    zip_code = serializers.CharField(max_length=20)

    def validate_city_id(self, value):
        """Validate that city exists"""
        if not City.objects.filter(id=value).exists():
            raise serializers.ValidationError("City does not exist")
        return value

    def validate(self, attrs):
        """Validate the complete address"""
        city_id = attrs.get("city_id")
        if city_id:
            try:
                city = City.objects.select_related("state__country").get(id=city_id)
                attrs["city"] = city
            except City.DoesNotExist:
                raise serializers.ValidationError("Invalid city")
        return attrs


# Address search serializer
class AddressSearchSerializer(serializers.Serializer):
    """
    Serializer for address search functionality
    """

    query = serializers.CharField(max_length=255, required=False)
    country_id = serializers.IntegerField(required=False)
    state_id = serializers.IntegerField(required=False)
    city_id = serializers.IntegerField(required=False)

    def validate_country_id(self, value):
        if not Country.objects.filter(id=value).exists():
            raise serializers.ValidationError("Country does not exist")
        return value

    def validate_state_id(self, value):
        if not State.objects.filter(id=value).exists():
            raise serializers.ValidationError("State does not exist")
        return value

    def validate_city_id(self, value):
        if not City.objects.filter(id=value).exists():
            raise serializers.ValidationError("City does not exist")
        return value
