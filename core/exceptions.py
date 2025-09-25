from rest_framework.views import exception_handler
from rest_framework import status
from rest_framework.response import Response
from .response import APIResponse


def drf_exception_handler(exc, context):
    """
    Custom exception handler for Django REST Framework
    Provides standardized error responses for better frontend integration
    """
    # Get the standard error response
    response = exception_handler(exc, context)
    
    if response is not None:
        # Extract error details
        error_data = response.data
        status_code = response.status_code
        
        # Determine error message based on status code
        if status_code == status.HTTP_400_BAD_REQUEST:
            message = "Validation failed"
        elif status_code == status.HTTP_401_UNAUTHORIZED:
            message = "Authentication required"
        elif status_code == status.HTTP_403_FORBIDDEN:
            message = "Permission denied"
        elif status_code == status.HTTP_404_NOT_FOUND:
            message = "Resource not found"
        elif status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
            message = "Method not allowed"
        elif status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            message = "Too many requests"
        elif status_code >= 500:
            message = "Internal server error"
        else:
            message = "An error occurred"
        
        # Create standardized error response
        error_response = APIResponse.error(
            message=message,
            errors=error_data,
            status_code=status_code
        )
        
        return error_response
    
    return response