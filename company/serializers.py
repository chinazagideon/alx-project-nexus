"""
Company serializers
"""
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import Company
from address.serializers import AddressNestedSerializer, AddressCreateSerializer
from address.mixins import AddressSerializerMixin, AddressDisplayMixin


class CompanySerializer(AddressSerializerMixin, AddressDisplayMixin, serializers.ModelSerializer):
    """
    Serializer for the company model with address support
    """
    address = AddressNestedSerializer(write_only=True)
    address_id = serializers.IntegerField(write_only=True, required=False)
    
    # Address display fields
    full_address = serializers.SerializerMethodField()
    short_address = serializers.SerializerMethodField()
    city_state = serializers.SerializerMethodField()
    country_code = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = (
            "id",
            "name",
            "description",
            "address",
            "address_id",
            "full_address",
            "short_address", 
            "city_state",
            "country_code",
            "contact_details",
            "website",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at", "status")

    def validate(self, attrs):
        """
        Validate the company data
        """
        attrs = super().validate(attrs)
        
        # Validate address if provided
        if attrs.get('address_id'):
            self.validate_address_id(attrs['address_id'])
        
        return attrs


class CompanyCreateSerializer(AddressDisplayMixin, serializers.ModelSerializer):
    """
    Serializer for creating companies with address
    """
    address = AddressCreateSerializer(required=False)
    address_id = serializers.IntegerField(write_only=True, required=False)
    
    # Address display fields
    full_address = serializers.SerializerMethodField()
    short_address = serializers.SerializerMethodField()
    city_state = serializers.SerializerMethodField()
    country_code = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = (
            "id",
            "name",
            "description",
            "address",
            "address_id",
            "full_address",
            "short_address",
            "city_state", 
            "country_code",
            "contact_details",
            "website",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "status")

    def validate(self, attrs):
        """
        Validate the company data
        """
        # Validate address data if provided
        address_data = attrs.get('address')
        if address_data:
            from address.services import AddressService
            service = AddressService()
            validation_result = service.validate_address(address_data)
            
            if not validation_result['is_valid']:
                raise serializers.ValidationError({
                    'address': validation_result['errors']
                })
        
        return attrs
    
    def create(self, validated_data):
        """
        Create a new company with address
        """
        from address.services import AddressService
        
        address_data = validated_data.pop('address', None)
        address_id = validated_data.pop('address_id', None)
        
        # Handle address creation or assignment
        if address_data:
            service = AddressService()
            address, created = service.get_or_create_address(address_data)
            validated_data['address'] = address
        elif address_id:
            validated_data['address_id'] = address_id
        
        return Company.objects.create(**validated_data)