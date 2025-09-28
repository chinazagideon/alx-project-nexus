"""
Views for the upload app
"""

import logging

from drf_spectacular.openapi import OpenApiParameter
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.mixins import StandardAPIViewMixin
from core.pagination import DefaultPagination
from core.permissions_enhanced import IsUploadOwnerOrStaff
from core.response import APIResponse
from core.viewset_permissions import get_upload_permissions, get_upload_queryset

from .models import Upload, UploadType
from .serializers import UploadSerializer

logger = logging.getLogger(__name__)


class UploadViewSet(viewsets.ModelViewSet):
    """
    View for listing and creating files
    """

    serializer_class = UploadSerializer
    queryset = Upload.objects.all()

    def get_permissions(self):
        return get_upload_permissions(self)

    def get_queryset(self):
        """
        Get the queryset for the upload list
        """
        return get_upload_queryset(self)

    @extend_schema(
        operation_id="list_uploads",
        summary="List all uploads",
        description="List all uploads",
        tags=["uploads"],
    )
    def list(self, request):
        """
        List all uploads
        """
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(data=serializer.data, message="Uploads listed successfully")

    @extend_schema(
        operation_id="create_upload",
        summary="Upload a file",
        description="Upload a file to the system. Supports various file types including PDFs, documents, images, and spreadsheets.",
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "format": "binary",
                        "description": "The file to upload (max 5MB). Select a file using the file input.",
                        "example": "resume.pdf",
                    },
                    "name": {
                        "type": "string",
                        "description": "Name of the file with extension (must match uploaded file)",
                        "example": "my_resume.pdf",
                    },
                    "type": {
                        "type": "string",
                        "enum": ["resume", "cover_letter", "profile_picture", "profile_cover", "certificate", "kyc"],
                        "description": "Type of upload",
                        "example": "resume",
                    },
                    "thumbnail": {
                        "type": "string",
                        "format": "binary",
                        "description": "Optional thumbnail image (max 5MB)",
                        "example": "thumbnail.jpg",
                    },
                    "content_type": {
                        "type": "string",
                        "description": "Content type model name (optional, defaults to user)",
                        "example": "user",
                    },
                    "object_id": {
                        "type": "integer",
                        "description": "ID of the related object (optional, defaults to current user)",
                        "example": 39,
                    },
                },
                "required": ["file_path", "name", "type"],
            }
        },
        examples=[
            OpenApiExample(
                "Resume Upload",
                summary="Upload a resume",
                description="Example of uploading a resume file",
                value={"file_path": "[FILE]", "name": "john_doe_resume.pdf", "type": "resume"},
            ),
            OpenApiExample(
                "Profile Picture Upload",
                summary="Upload a profile picture",
                description="Example of uploading a profile picture with thumbnail",
                value={"file_path": "[FILE]", "name": "profile_photo.jpg", "type": "profile_picture", "thumbnail": "[FILE]"},
            ),
        ],
        responses={
            201: {
                "description": "File uploaded successfully",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "success": {"type": "boolean"},
                                "message": {"type": "string"},
                                "data": {
                                    "type": "object",
                                    "properties": {
                                        "id": {"type": "integer"},
                                        "name": {"type": "string"},
                                        "type": {"type": "string"},
                                        "file_url": {"type": "string"},
                                        "file_size": {"type": "integer"},
                                        "created_at": {"type": "string", "format": "date-time"},
                                    },
                                },
                            },
                        }
                    }
                },
            },
            400: {
                "description": "Bad request - validation error",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "success": {"type": "boolean"},
                                "message": {"type": "string"},
                                "error": {"type": "string"},
                            },
                        }
                    }
                },
            },
        },
        tags=["uploads"],
    )
    def create(self, request):
        """
        Create a new upload
        """
        try:
            # Debug logging
            logger.info(f"Request data: {request.data}")
            logger.info(f"Request FILES: {list(request.FILES.keys())}")

            # Check if file is provided
            if "file_path" not in request.FILES:
                return Response(
                    {"success": False, "message": "No file provided", "error": "file_path field is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Validate file size (5MB limit)
            file = request.FILES["file_path"]
            logger.info(f"File details: name={file.name}, size={file.size}, content_type={file.content_type}")

            if file.size > 5 * 1024 * 1024:  # 5MB
                return Response(
                    {"success": False, "message": "File too large", "error": "File size must be less than 5MB"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Prepare data for serializer
            data = {}

            # Extract values from QueryDict (remove lists)
            for key, value in request.data.items():
                if isinstance(value, list) and len(value) > 0:
                    data[key] = value[0]  # Take first value from list
                else:
                    data[key] = value

            # Set the file from FILES to data
            data["file_path"] = file

            # If thumbnail is provided, add it too
            if "thumbnail" in request.FILES:
                data["thumbnail"] = request.FILES["thumbnail"]

            logger.info(f"Data for serializer: {data}")

            serializer = self.get_serializer(data=data)
            logger.info(f"Serializer created, validating...")

            try:
                is_valid = serializer.is_valid()
                logger.info(f"Serializer validation result: {is_valid}")
            except Exception as validation_error:
                logger.error(f"Error during validation: {str(validation_error)}")
                return Response(
                    {"success": False, "message": "Validation error", "error": str(validation_error)},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if serializer.is_valid():
                logger.info(f"Serializer is valid, saving...")
                try:
                    upload = serializer.save()
                    logger.info(f"Upload saved successfully: {upload}")

                    # Return success response with upload details
                    return Response(
                        {
                            "success": True,
                            "message": "File uploaded successfully",
                            "data": {
                                "id": upload.id,
                                "name": upload.name,
                                "type": upload.type,
                                "file_url": request.build_absolute_uri(upload.file_path.url) if upload.file_path else None,
                                "file_size": upload.file_path.size if upload.file_path else None,
                                "created_at": upload.created_at.isoformat(),
                            },
                        },
                        status=status.HTTP_201_CREATED,
                    )
                except Exception as save_error:
                    logger.error(f"Error saving upload: {str(save_error)}")
                    return Response(
                        {"success": False, "message": "Failed to save upload", "error": str(save_error)},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                # Return validation errors
                logger.error(f"Serializer validation errors: {serializer.errors}")
                return Response(
                    {"success": False, "message": "Validation failed", "errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except Exception as e:
            logger.error(f"Error creating upload: {str(e)}")
            return Response(
                {"success": False, "message": "Failed to upload file", "error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        operation_id="retrieve_upload",
        summary="Retrieve a upload",
        description="Retrieve a upload",
        responses={200: UploadSerializer},
        tags=["uploads"],
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a upload
        """
        return super().retrieve(request, *args, **kwargs)
