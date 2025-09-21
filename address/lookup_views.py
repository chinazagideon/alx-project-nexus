"""
Address lookup and utility views
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import (
    CountryLookupSerializer,
    StateLookupSerializer,
    CityLookupSerializer,
    AddressValidationSerializer,
)
from .services import AddressService, AddressLookupService
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes


@extend_schema(
    operation_id='address_lookup_countries',
    summary='Get Countries',
    description='Get list of all countries for address lookups',
    responses={
        200: CountryLookupSerializer(many=True),
    },
    tags=['addresses']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_countries(request):
    """
    Get all countries for address lookups
    """
    countries = AddressLookupService.get_countries()
    return Response(countries)


@extend_schema(
    operation_id='address_lookup_states',
    summary='Get States by Country',
    description='Get list of states for a specific country',
    parameters=[
        OpenApiParameter(
            name='country_id',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='Country ID to filter states',
            required=True
        )
    ],
    responses={
        200: StateLookupSerializer(many=True),
    },
    tags=['addresses']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_states_by_country(request):
    """
    Get states by country ID
    """
    country_id = request.query_params.get('country_id')
    if not country_id:
        return Response(
            {'error': 'country_id parameter is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        states = AddressLookupService.get_states_by_country(int(country_id))
        return Response(states)
    except ValueError:
        return Response(
            {'error': 'Invalid country_id'},
            status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema(
    operation_id='address_lookup_cities',
    summary='Get Cities by State',
    description='Get list of cities for a specific state',
    parameters=[
        OpenApiParameter(
            name='state_id',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='State ID to filter cities',
            required=True
        )
    ],
    responses={
        200: CityLookupSerializer(many=True),
    },
    tags=['addresses']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_cities_by_state(request):
    """
    Get cities by state ID
    """
    state_id = request.query_params.get('state_id')
    if not state_id:
        return Response(
            {'error': 'state_id parameter is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        cities = AddressLookupService.get_cities_by_state(int(state_id))
        return Response(cities)
    except ValueError:
        return Response(
            {'error': 'Invalid state_id'},
            status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema(
    operation_id='address_search_locations',
    summary='Search Locations',
    description='Search across countries, states, and cities',
    parameters=[
        OpenApiParameter(
            name='q',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Search query',
            required=True
        ),
        OpenApiParameter(
            name='limit',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='Maximum number of results',
            default=20
        )
    ],
    responses={
        200: {
            'type': 'object',
            'properties': {
                'results': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'type': {'type': 'string', 'enum': ['country', 'state', 'city']},
                            'id': {'type': 'integer'},
                            'name': {'type': 'string'},
                            'parent': {'type': 'string'},
                            'full_name': {'type': 'string'}
                        }
                    }
                }
            }
        }
    },
    tags=['addresses']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def search_locations(request):
    """
    Search across all location types
    """
    query = request.query_params.get('q', '')
    limit = int(request.query_params.get('limit', 20))
    
    if len(query) < 2:
        return Response({'results': []})
    
    results = AddressLookupService.search_locations(query, limit)
    return Response({'results': results})


@extend_schema(
    operation_id='address_validate',
    summary='Validate Address',
    description='Validate address data and get suggestions',
    request=AddressValidationSerializer,
    responses={
        200: {
            'type': 'object',
            'properties': {
                'is_valid': {'type': 'boolean'},
                'errors': {'type': 'array', 'items': {'type': 'string'}},
                'suggestions': {'type': 'array', 'items': {'type': 'string'}},
                'normalized_address': {
                    'type': 'object',
                    'properties': {
                        'location': {'type': 'string'},
                        'city': {'type': 'string'},
                        'state': {'type': 'string'},
                        'country': {'type': 'string'},
                        'zip_code': {'type': 'string'}
                    }
                }
            }
        }
    },
    tags=['addresses']
)
@api_view(['POST'])
@permission_classes([AllowAny])
def validate_address(request):
    """
    Validate address data
    """
    serializer = AddressValidationSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    service = AddressService()
    result = service.validate_address(serializer.validated_data)
    
    return Response(result)


@extend_schema(
    operation_id='address_hierarchy',
    summary='Get Address Hierarchy',
    description='Get complete address hierarchy for cascading dropdowns',
    parameters=[
        OpenApiParameter(
            name='country_id',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='Optional country ID to filter states'
        ),
        OpenApiParameter(
            name='state_id',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='Optional state ID to filter cities'
        )
    ],
    responses={
        200: {
            'type': 'object',
            'properties': {
                'countries': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer'},
                            'name': {'type': 'string'},
                            'code': {'type': 'string'}
                        }
                    }
                },
                'states': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer'},
                            'name': {'type': 'string'},
                            'country_id': {'type': 'integer'}
                        }
                    }
                },
                'cities': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer'},
                            'name': {'type': 'string'},
                            'state_id': {'type': 'integer'}
                        }
                    }
                }
            }
        }
    },
    tags=['addresses']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_address_hierarchy(request):
    """
    Get complete address hierarchy
    """
    service = AddressService()
    country_id = request.query_params.get('country_id')
    state_id = request.query_params.get('state_id')
    
    if country_id:
        country_id = int(country_id)
    if state_id:
        state_id = int(state_id)
    
    hierarchy = service.get_address_hierarchy(country_id, state_id)
    return Response(hierarchy)


@extend_schema(
    operation_id='address_statistics',
    summary='Get Address Statistics',
    description='Get address-related statistics',
    responses={
        200: {
            'type': 'object',
            'properties': {
                'total_addresses': {'type': 'integer'},
                'total_cities': {'type': 'integer'},
                'total_states': {'type': 'integer'},
                'total_countries': {'type': 'integer'},
                'countries_with_addresses': {'type': 'integer'}
            }
        }
    },
    tags=['addresses']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_address_statistics(request):
    """
    Get address statistics
    """
    service = AddressService()
    stats = service.get_address_statistics()
    return Response(stats)
