# Address Module - Robust Address Solution

This module provides a comprehensive address solution that avoids redundancy while allowing other endpoints to receive address data efficiently.

## Features

- **Nested Address Serializers**: For displaying address data in related entities
- **Address Lookup Services**: For cascading dropdowns and autocomplete
- **Address Validation**: For validating address data before creation
- **Address Mixins**: For reusable functionality across different models
- **Caching**: For improved performance on lookup operations
- **Comprehensive API**: Full CRUD + lookup endpoints

## Quick Start

### 1. Using Address in Your Serializers

```python
from address.serializers import AddressNestedSerializer, AddressCreateSerializer
from address.mixins import AddressSerializerMixin, AddressDisplayMixin

class YourModelSerializer(AddressSerializerMixin, AddressDisplayMixin, serializers.ModelSerializer):
    address = AddressNestedSerializer(read_only=True)
    address_id = serializers.IntegerField(write_only=True, required=False)
    
    # Address display fields (automatically added by mixin)
    full_address = serializers.SerializerMethodField()
    short_address = serializers.SerializerMethodField()
    city_state = serializers.SerializerMethodField()
    country_code = serializers.SerializerMethodField()
    
    class Meta:
        model = YourModel
        fields = (
            'id',
            'name',
            'address',
            'address_id',
            'full_address',
            'short_address',
            'city_state',
            'country_code',
            # ... other fields
        )
```

### 2. Creating Entities with Address

```python
class YourModelCreateSerializer(serializers.ModelSerializer):
    address = AddressCreateSerializer(required=False)
    address_id = serializers.IntegerField(write_only=True, required=False)
    
    def create(self, validated_data):
        from address.services import AddressService
        
        address_data = validated_data.pop('address', None)
        address_id = validated_data.pop('address_id', None)
        
        if address_data:
            service = AddressService()
            address, created = service.get_or_create_address(address_data)
            validated_data['address'] = address
        elif address_id:
            validated_data['address_id'] = address_id
        
        return YourModel.objects.create(**validated_data)
```

### 3. Using Address Lookup Endpoints

```javascript
// Get countries
GET /api/addresses/lookup/countries/

// Get states by country
GET /api/addresses/lookup/states/?country_id=1

// Get cities by state
GET /api/addresses/lookup/cities/?state_id=1

// Search locations
GET /api/addresses/lookup/search/?q=New York&limit=10

// Get complete hierarchy
GET /api/addresses/lookup/hierarchy/

// Validate address
POST /api/addresses/validate/
{
    "location": "123 Main St",
    "city_id": 1,
    "zip_code": "12345"
}
```

## API Endpoints

### CRUD Endpoints
- `GET /api/addresses/addresses/` - List addresses
- `POST /api/addresses/addresses/` - Create address
- `GET /api/addresses/addresses/{id}/` - Get address
- `PUT /api/addresses/addresses/{id}/` - Update address
- `DELETE /api/addresses/addresses/{id}/` - Delete address

### Lookup Endpoints
- `GET /api/addresses/lookup/countries/` - Get all countries
- `GET /api/addresses/lookup/states/?country_id=1` - Get states by country
- `GET /api/addresses/lookup/cities/?state_id=1` - Get cities by state
- `GET /api/addresses/lookup/search/?q=query` - Search locations
- `GET /api/addresses/lookup/hierarchy/` - Get complete hierarchy
- `POST /api/addresses/validate/` - Validate address
- `GET /api/addresses/statistics/` - Get address statistics

## Serializers

### AddressNestedSerializer
For displaying address data in related entities:
```python
{
    "id": 1,
    "location": "123 Main St",
    "city_name": "New York",
    "state_name": "NY",
    "country_name": "United States",
    "country_code": "US",
    "zip_code": "10001"
}
```

### AddressCreateSerializer
For creating addresses with nested data:
```python
{
    "location": "123 Main St",
    "city_id": 1,
    "zip_code": "10001"
}
```

## Services

### AddressService
Main service for address operations:
```python
from address.services import AddressService

service = AddressService()

# Get or create address
address, created = service.get_or_create_address({
    'location': '123 Main St',
    'city_id': 1,
    'zip_code': '10001'
})

# Validate address
result = service.validate_address(address_data)

# Search addresses
addresses = service.search_addresses('New York')

# Get hierarchy
hierarchy = service.get_address_hierarchy(country_id=1)
```

### AddressLookupService
Service for lookup operations:
```python
from address.services import AddressLookupService

# Get countries
countries = AddressLookupService.get_countries()

# Get states by country
states = AddressLookupService.get_states_by_country(1)

# Get cities by state
cities = AddressLookupService.get_cities_by_state(1)

# Search locations
results = AddressLookupService.search_locations('New York')
```

## Mixins

### AddressSerializerMixin
Adds address fields and validation to serializers:
```python
class YourSerializer(AddressSerializerMixin, serializers.ModelSerializer):
    # Automatically adds address fields and validation
    pass
```

### AddressDisplayMixin
Adds address display methods:
```python
class YourSerializer(AddressDisplayMixin, serializers.ModelSerializer):
    # Adds get_full_address, get_short_address, etc.
    pass
```

### AddressFilterMixin
Adds address filtering to viewsets:
```python
class YourViewSet(AddressFilterMixin, viewsets.ModelViewSet):
    def get_queryset(self):
        queryset = super().get_queryset()
        return self.apply_address_filters(queryset, self.request)
```

## Best Practices

1. **Use AddressNestedSerializer for display**: When showing address data in related entities
2. **Use AddressCreateSerializer for creation**: When creating new addresses
3. **Use mixins for consistency**: Apply the same address functionality across models
4. **Validate addresses**: Always validate address data before saving
5. **Use lookup endpoints**: For cascading dropdowns and autocomplete
6. **Cache lookups**: The service automatically caches lookup data for performance

## Example Usage in Frontend

```javascript
// Cascading dropdowns
const loadStates = async (countryId) => {
    const response = await fetch(`/api/addresses/lookup/states/?country_id=${countryId}`);
    return response.json();
};

const loadCities = async (stateId) => {
    const response = await fetch(`/api/addresses/lookup/cities/?state_id=${stateId}`);
    return response.json();
};

// Address autocomplete
const searchLocations = async (query) => {
    const response = await fetch(`/api/addresses/lookup/search/?q=${query}`);
    return response.json();
};

// Validate address before submission
const validateAddress = async (addressData) => {
    const response = await fetch('/api/addresses/validate/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(addressData)
    });
    return response.json();
};
```

## Performance Considerations

- **Caching**: Lookup data is cached for 5 minutes by default
- **Database queries**: Use `select_related` for address relationships
- **Pagination**: Use pagination for large address lists
- **Indexing**: Ensure proper database indexes on address fields

## Error Handling

The address system provides comprehensive error handling:
- Validation errors for invalid data
- 400 errors for missing required parameters
- 404 errors for non-existent addresses
- Detailed error messages for debugging

This robust address solution eliminates redundancy while providing a comprehensive set of tools for handling addresses across your application.
