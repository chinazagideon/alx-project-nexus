"""
Mixins for standardized API responses
"""

from rest_framework import viewsets, status
from rest_framework.response import Response
from .response import APIResponse


class StandardResponseMixin:
    """
    Mixin to provide standardized API responses for ViewSets
    """

    def create(self, request, *args, **kwargs):
        """
        Create a new instance with standardized response
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        # Get the serializer for response (might be different from create serializer)
        response_serializer = self.get_serializer(instance)

        return APIResponse.created(data=response_serializer.data, message=f"{self.get_verbose_name()} created successfully")

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve an instance with standardized response
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        return APIResponse.success(data=serializer.data, message=f"{self.get_verbose_name()} retrieved successfully")

    def update(self, request, *args, **kwargs):
        """
        Update an instance with standardized response
        """
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        return APIResponse.success(data=serializer.data, message=f"{self.get_verbose_name()} updated successfully")

    def destroy(self, request, *args, **kwargs):
        """
        Delete an instance with standardized response
        """
        instance = self.get_object()
        instance.delete()

        return APIResponse.success(
            data=None, message=f"{self.get_verbose_name()} deleted successfully", status_code=status.HTTP_204_NO_CONTENT
        )

    def list(self, request, *args, **kwargs):
        """
        List instances with standardized response
        """
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_response = self.get_paginated_response(serializer.data)

            # Wrap paginated response
            return APIResponse.success(
                data=paginated_response.data, message=f"{self.get_verbose_name_plural()} retrieved successfully"
            )

        serializer = self.get_serializer(queryset, many=True)

        return APIResponse.success(data=serializer.data, message=f"{self.get_verbose_name_plural()} retrieved successfully")

    def get_verbose_name(self):
        """
        Get the verbose name of the model
        Override this method in your ViewSet if needed
        """
        if hasattr(self, "queryset") and self.queryset.model:
            return self.queryset.model._meta.verbose_name.title()
        return "Resource"

    def get_verbose_name_plural(self):
        """
        Get the plural verbose name of the model
        Override this method in your ViewSet if needed
        """
        if hasattr(self, "queryset") and self.queryset.model:
            return self.queryset.model._meta.verbose_name_plural.title()
        return "Resources"


class StandardAPIViewMixin:
    """
    Mixin for APIView classes to use standardized responses
    """

    def success_response(self, data=None, message="Request completed successfully", status_code=status.HTTP_200_OK, **kwargs):
        """
        Create a success response
        """
        return APIResponse.success(data=data, message=message, status_code=status_code, **kwargs)

    def error_response(self, message="An error occurred", errors=None, status_code=status.HTTP_400_BAD_REQUEST, **kwargs):
        """
        Create an error response
        """
        return APIResponse.error(message=message, errors=errors, status_code=status_code, **kwargs)

    def validation_error_response(self, errors, message="Validation failed", **kwargs):
        """
        Create a validation error response
        """
        return APIResponse.validation_error(errors=errors, message=message, **kwargs)

    def not_found_response(self, message="Resource not found", **kwargs):
        """
        Create a not found response
        """
        return APIResponse.not_found(message=message, **kwargs)

    def created_response(self, data=None, message="Resource created successfully", **kwargs):
        """
        Create a created response
        """
        return APIResponse.created(data=data, message=message, **kwargs)
