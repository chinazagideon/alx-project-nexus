"""
Address mixins for reusable functionality across different models
"""
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .serializers import AddressNestedSerializer, AddressCreateSerializer
from .services import AddressService


class AddressMixin:
    """
    Mixin to add address functionality to any model
    """
    
    def get_address_serializer_class(self):
        """Override this method to customize address serializer"""
        return AddressNestedSerializer
    
    def get_address_create_serializer_class(self):
        """Override this method to customize address creation serializer"""
        return AddressCreateSerializer


class AddressFieldMixin:
    """
    Mixin to add address fields to serializers
    """
    
    def get_address_fields(self):
        """Get address fields for the serializer"""
        return {
            'address': AddressNestedSerializer(read_only=True),
            'address_id': serializers.IntegerField(write_only=True, required=False),
        }
    
    def get_address_create_fields(self):
        """Get address creation fields for the serializer"""
        return {
            'address': AddressCreateSerializer(required=False),
            'address_id': serializers.IntegerField(write_only=True, required=False),
        }


class AddressValidationMixin:
    """
    Mixin to add address validation to serializers
    """
    
    def validate_address_id(self, value):
        """Validate that address exists"""
        from .models import Address
        if not Address.objects.filter(id=value, status=True).exists():
            raise serializers.ValidationError("Address does not exist or is inactive")
        return value
    
    def validate_address_data(self, address_data):
        """Validate address data using AddressService"""
        if not address_data:
            return None
        
        service = AddressService()
        validation_result = service.validate_address(address_data)
        
        if not validation_result['is_valid']:
            raise serializers.ValidationError({
                'address': validation_result['errors']
            })
        
        return validation_result['normalized_address']


class AddressLookupMixin:
    """
    Mixin to add address lookup functionality to views
    """
    
    def get_address_hierarchy(self, request):
        """Get address hierarchy for cascading dropdowns"""
        from .services import AddressService
        
        service = AddressService()
        country_id = request.query_params.get('country_id')
        state_id = request.query_params.get('state_id')
        
        if country_id:
            country_id = int(country_id)
        if state_id:
            state_id = int(state_id)
        
        return service.get_address_hierarchy(country_id, state_id)
    
    def get_location_suggestions(self, request):
        """Get location suggestions for autocomplete"""
        from .services import AddressService
        
        service = AddressService()
        query = request.query_params.get('q', '')
        limit = int(request.query_params.get('limit', 10))
        
        return service.get_location_suggestions(query, limit)


class AddressSerializerMixin(AddressFieldMixin, AddressValidationMixin):
    """
    Complete mixin combining address fields and validation
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add address fields to the serializer
        address_fields = self.get_address_fields()
        for field_name, field in address_fields.items():
            self.fields[field_name] = field
    
    def validate(self, attrs):
        """Validate address data if provided"""
        attrs = super().validate(attrs)
        
        # Validate address if address_id is provided
        if attrs.get('address_id'):
            self.validate_address_id(attrs['address_id'])
        
        return attrs


class AddressCreateSerializerMixin(AddressFieldMixin, AddressValidationMixin):
    """
    Mixin for creating entities with address data
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add address creation fields to the serializer
        address_fields = self.get_address_create_fields()
        for field_name, field in address_fields.items():
            self.fields[field_name] = field
    
    def validate(self, attrs):
        """Validate address data if provided"""
        attrs = super().validate(attrs)
        
        # Handle address creation
        address_data = attrs.get('address')
        if address_data:
            validated_address = self.validate_address_data(address_data)
            if validated_address:
                attrs['address_data'] = validated_address
        
        return attrs
    
    def create(self, validated_data):
        """Create entity with address"""
        from .services import AddressService
        
        address_data = validated_data.pop('address_data', None)
        address_id = validated_data.pop('address_id', None)
        
        # Handle address creation or assignment
        if address_data:
            service = AddressService()
            address, created = service.get_or_create_address(address_data)
            validated_data['address'] = address
        elif address_id:
            validated_data['address_id'] = address_id
        
        return super().create(validated_data)


class AddressDisplayMixin:
    """
    Mixin to add address display functionality
    """
    
    @extend_schema_field(serializers.CharField())
    def get_full_address(self, obj):
        """Get full address string"""
        if not hasattr(obj, 'address') or not obj.address:
            return None
        
        address = obj.address
        return f"{address.location}, {address.city.name}, {address.city.state.name}, {address.city.state.country.name} {address.zip_code}"
    
    @extend_schema_field(serializers.CharField())
    def get_short_address(self, obj):
        """Get short address string"""
        if not hasattr(obj, 'address') or not obj.address:
            return None
        
        address = obj.address
        return f"{address.city.name}, {address.city.state.name}"
    
    @extend_schema_field(serializers.CharField())
    def get_city_state(self, obj):
        """Get city and state only"""
        if not hasattr(obj, 'address') or not obj.address:
            return None
        
        address = obj.address
        return f"{address.city.name}, {address.city.state.name}"
    
    @extend_schema_field(serializers.CharField())
    def get_country_code(self, obj):
        """Get country code"""
        if not hasattr(obj, 'address') or not obj.address:
            return None
        
        return obj.address.city.state.country.code


class AddressFilterMixin:
    """
    Mixin to add address filtering to viewsets
    """
    
    def get_address_filters(self, request):
        """Get address-related filters from request"""
        filters = {}
        
        country_id = request.query_params.get('country_id')
        state_id = request.query_params.get('state_id')
        city_id = request.query_params.get('city_id')
        location = request.query_params.get('location')
        
        if country_id:
            filters['address__city__state__country_id'] = country_id
        if state_id:
            filters['address__city__state_id'] = state_id
        if city_id:
            filters['address__city_id'] = city_id
        if location:
            filters['address__location__icontains'] = location
        
        return filters
    
    def apply_address_filters(self, queryset, request):
        """Apply address filters to queryset"""
        filters = self.get_address_filters(request)
        return queryset.filter(**filters)
