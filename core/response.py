"""
Standardized API response utilities for consistent frontend integration
"""
from rest_framework import status
from rest_framework.response import Response
from typing import Any, Dict, Optional, Union
from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers


class APIResponseSerializer(serializers.Serializer):
    """
    Standardized API response serializer for DRF documentation
    """
    success = serializers.BooleanField(help_text="Indicates if the request was successful")
    message = serializers.CharField(help_text="Human-readable message describing the result")
    data = serializers.JSONField(help_text="Response data payload", allow_null=True)
    status_code = serializers.IntegerField(help_text="HTTP status code")
    errors = serializers.DictField(help_text="Validation errors (only present when success is false)", required=False)


class ErrorResponseSerializer(serializers.Serializer):
    """
    Standardized error response serializer for DRF documentation
    """
    success = serializers.BooleanField(default=False, help_text="Always false for error responses")
    message = serializers.CharField(help_text="Error message")
    errors = serializers.DictField(help_text="Detailed error information", required=False)
    status_code = serializers.IntegerField(help_text="HTTP status code")


# Pre-defined response serializers for DRF documentation
class SuccessResponseSerializer(serializers.Serializer):
    """
    Standardized success response serializer for DRF documentation
    """
    success = serializers.BooleanField(default=True, help_text="Always true for success responses")
    message = serializers.CharField(help_text="Success message")
    data = serializers.JSONField(help_text="Response data payload", allow_null=True)
    status_code = serializers.IntegerField(help_text="HTTP status code")


class ErrorResponseSerializer(serializers.Serializer):
    """
    Standardized error response serializer for DRF documentation
    """
    success = serializers.BooleanField(default=False, help_text="Always false for error responses")
    message = serializers.CharField(help_text="Error message")
    data = serializers.JSONField(default=None, help_text="Always null for error responses")
    status_code = serializers.IntegerField(help_text="HTTP status code")
    errors = serializers.DictField(help_text="Detailed error information", required=False)


class ValidationErrorResponseSerializer(serializers.Serializer):
    """
    Standardized validation error response serializer for DRF documentation
    """
    success = serializers.BooleanField(default=False, help_text="Always false for validation errors")
    message = serializers.CharField(default="Validation failed", help_text="Error message")
    data = serializers.JSONField(default=None, help_text="Always null for error responses")
    status_code = serializers.IntegerField(default=400, help_text="HTTP status code")
    errors = serializers.DictField(
        child=serializers.ListField(child=serializers.CharField()),
        help_text="Validation errors by field"
    )


# Factory functions for creating response serializers for documentation
def create_success_response_serializer(data_serializer=None, message="Request completed successfully", status_code=200):
    """
    Create a success response serializer for DRF documentation
    """
    msg = message
    code = status_code
    data_field = data_serializer if data_serializer else serializers.JSONField(help_text="Response data payload", allow_null=True)
    
    class DynamicSuccessResponseSerializer(serializers.Serializer):
        success = serializers.BooleanField(default=True, help_text="Always true for success responses")
        message = serializers.CharField(default=msg, help_text="Success message")
        data = data_field
        status_code = serializers.IntegerField(default=code, help_text="HTTP status code")
    
    return DynamicSuccessResponseSerializer


def create_error_response_serializer(message="An error occurred", status_code=400):
    """
    Create an error response serializer for DRF documentation
    """
    msg = message
    code = status_code
    
    class DynamicErrorResponseSerializer(serializers.Serializer):
        success = serializers.BooleanField(default=False, help_text="Always false for error responses")
        message = serializers.CharField(default=msg, help_text="Error message")
        data = serializers.JSONField(default=None, help_text="Always null for error responses")
        status_code = serializers.IntegerField(default=code, help_text="HTTP status code")
        errors = serializers.DictField(help_text="Detailed error information", required=False)
    
    return DynamicErrorResponseSerializer


def create_validation_error_response_serializer():
    """
    Create a validation error response serializer for DRF documentation
    """
    class DynamicValidationErrorResponseSerializer(serializers.Serializer):
        success = serializers.BooleanField(default=False, help_text="Always false for validation errors")
        message = serializers.CharField(default="Validation failed", help_text="Error message")
        data = serializers.JSONField(default=None, help_text="Always null for error responses")
        status_code = serializers.IntegerField(default=400, help_text="HTTP status code")
        errors = serializers.DictField(
            child=serializers.ListField(child=serializers.CharField()),
            help_text="Validation errors by field"
        )
    
    return DynamicValidationErrorResponseSerializer


class APIResponse:
    """
    Standardized API response class for consistent frontend integration
    """
    
    @staticmethod
    def success(
        data: Any = None,
        message: str = "Request completed successfully",
        status_code: int = status.HTTP_200_OK,
        **kwargs
    ) -> Response:
        """
        Create a successful API response
        
        Args:
            data: Response data payload
            message: Success message
            status_code: HTTP status code
            **kwargs: Additional response fields
            
        Returns:
            Response: Standardized success response
        """
        response_data = {
            "success": True,
            "message": message,
            "data": data,
            "status_code": status_code,
        }
        
        # Add any additional fields
        response_data.update(kwargs)
        
        return Response(response_data, status=status_code)
    
    @staticmethod
    def created(
        data: Any = None,
        message: str = "Resource created successfully",
        **kwargs
    ) -> Response:
        """
        Create a 201 Created response
        
        Args:
            data: Created resource data
            message: Success message
            **kwargs: Additional response fields
            
        Returns:
            Response: 201 Created response
        """
        return APIResponse.success(
            data=data,
            message=message,
            status_code=status.HTTP_201_CREATED,
            **kwargs
        )
    
    @staticmethod
    def no_content(
        message: str = "Request completed successfully",
        **kwargs
    ) -> Response:
        """
        Create a 204 No Content response
        
        Args:
            message: Success message
            **kwargs: Additional response fields
            
        Returns:
            Response: 204 No Content response
        """
        return APIResponse.success(
            data=None,
            message=message,
            status_code=status.HTTP_204_NO_CONTENT,
            **kwargs
        )
    
    @staticmethod
    def error(
        message: str = "An error occurred",
        errors: Optional[Dict] = None,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        **kwargs
    ) -> Response:
        """
        Create an error API response
        
        Args:
            message: Error message
            errors: Detailed error information
            status_code: HTTP status code
            **kwargs: Additional response fields
            
        Returns:
            Response: Standardized error response
        """
        response_data = {
            "success": False,
            "message": message,
            "data": None,
            "status_code": status_code,
        }
        
        if errors:
            response_data["errors"] = errors
            
        # Add any additional fields
        response_data.update(kwargs)
        
        return Response(response_data, status=status_code)
    
    @staticmethod
    def validation_error(
        errors: Dict,
        message: str = "Validation failed",
        **kwargs
    ) -> Response:
        """
        Create a validation error response
        
        Args:
            errors: Validation errors dictionary
            message: Error message
            **kwargs: Additional response fields
            
        Returns:
            Response: 400 Bad Request with validation errors
        """
        return APIResponse.error(
            message=message,
            errors=errors,
            status_code=status.HTTP_400_BAD_REQUEST,
            **kwargs
        )
    
    @staticmethod
    def not_found(
        message: str = "Resource not found",
        **kwargs
    ) -> Response:
        """
        Create a 404 Not Found response
        
        Args:
            message: Error message
            **kwargs: Additional response fields
            
        Returns:
            Response: 404 Not Found response
        """
        return APIResponse.error(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            **kwargs
        )
    
    @staticmethod
    def unauthorized(
        message: str = "Authentication required",
        **kwargs
    ) -> Response:
        """
        Create a 401 Unauthorized response
        
        Args:
            message: Error message
            **kwargs: Additional response fields
            
        Returns:
            Response: 401 Unauthorized response
        """
        return APIResponse.error(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            **kwargs
        )
    
    @staticmethod
    def forbidden(
        message: str = "Permission denied",
        **kwargs
    ) -> Response:
        """
        Create a 403 Forbidden response
        
        Args:
            message: Error message
            **kwargs: Additional response fields
            
        Returns:
            Response: 403 Forbidden response
        """
        return APIResponse.error(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            **kwargs
        )
    
    @staticmethod
    def server_error(
        message: str = "Internal server error",
        **kwargs
    ) -> Response:
        """
        Create a 500 Internal Server Error response
        
        Args:
            message: Error message
            **kwargs: Additional response fields
            
        Returns:
            Response: 500 Internal Server Error response
        """
        return APIResponse.error(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            **kwargs
        )


# Decorator for automatic response wrapping
def api_response(success_message: str = "Request completed successfully"):
    """
    Decorator to automatically wrap view responses with standardized format
    
    Args:
        success_message: Default success message for the endpoint
    """
    def decorator(view_func):
        def wrapper(self, request, *args, **kwargs):
            try:
                response = view_func(self, request, *args, **kwargs)
                
                # If response is already a Response object, wrap it
                if isinstance(response, Response):
                    # Check if it's already wrapped
                    if 'success' in response.data:
                        return response
                    
                    # Wrap the response
                    wrapped_data = {
                        "success": True,
                        "message": success_message,
                        "data": response.data,
                        "status_code": response.status_code,
                    }
                    return Response(wrapped_data, status=response.status_code)
                
                # If it's raw data, wrap it
                wrapped_data = {
                    "success": True,
                    "message": success_message,
                    "data": response,
                    "status_code": status.HTTP_200_OK,
                }
                return Response(wrapped_data)
                
            except Exception as e:
                return APIResponse.error(
                    message=f"An error occurred: {str(e)}",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return wrapper
    return decorator
