"""
Email verification views and utilities
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.utils import timezone
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from core.response import APIResponse
from core.mixins import StandardAPIViewMixin
from drf_spectacular.utils import extend_schema
from .models.models import User
import logging

logger = logging.getLogger(__name__)


class EmailVerificationView(StandardAPIViewMixin, APIView):
    """
    Handle email verification via token
    """
    permission_classes = [AllowAny]

    @extend_schema(
        operation_id='verify_email',
        summary='Verify user email',
        description='Verify user email address using verification token',
        tags=['Auth'],
        responses={
            200: {
                'description': 'Email verified successfully',
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'object',
                            'properties': {
                                'success': {'type': 'boolean'},
                                'message': {'type': 'string'},
                                'data': {
                                    'type': 'object',
                                    'properties': {
                                        'user_id': {'type': 'integer'},
                                        'email': {'type': 'string'},
                                        'is_verified': {'type': 'boolean'}
                                    }
                                }
                            }
                        }
                    }
                }
            },
            400: {
                'description': 'Invalid or expired token',
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'object',
                            'properties': {
                                'success': {'type': 'boolean'},
                                'message': {'type': 'string'},
                                'error': {'type': 'string'}
                            }
                        }
                    }
                }
            }
        }
    )
    def get(self, request):
        """
        Verify email using token from query parameter
        """
        token = request.GET.get('token')
        
        if not token:
            return self.error_response(
                message="Verification token is required",
                error="MISSING_TOKEN",
                status_code=400
            )
        
        try:
            # Find user by verification token
            user = User.objects.get(email_verification_token=token)
            
            # Check if already verified
            if user.is_email_verified:
                return self.success_response(
                    data={
                        'user_id': user.id,
                        'email': user.email,
                        'is_verified': True
                    },
                    message="Email is already verified"
                )
            
            # Check if token is expired (24 hours)
            if user.email_verification_sent_at:
                time_diff = timezone.now() - user.email_verification_sent_at
                if time_diff.total_seconds() > 24 * 60 * 60:  # 24 hours
                    return self.error_response(
                        message="Verification token has expired. Please request a new one.",
                        error="TOKEN_EXPIRED",
                        status_code=400
                    )
            
            # Verify the email
            user.is_email_verified = True
            user.save(update_fields=['is_email_verified'])
            
            logger.info(f"Email verified for user {user.id} ({user.email})")
            
            return self.success_response(
                data={
                    'user_id': user.id,
                    'email': user.email,
                    'is_verified': True
                },
                message="Email verified successfully"
            )
            
        except User.DoesNotExist:
            return self.error_response(
                message="Invalid verification token",
                error="INVALID_TOKEN",
                status_code=400
            )
        except Exception as e:
            logger.error(f"Error verifying email: {str(e)}")
            return self.error_response(
                message="An error occurred during verification",
                error="VERIFICATION_ERROR",
                status_code=500
            )


class ResendVerificationView(StandardAPIViewMixin, APIView):
    """
    Resend email verification
    """
    permission_classes = [AllowAny]

    @extend_schema(
        operation_id='resend_verification',
        summary='Resend email verification',
        description='Resend email verification to user',
        tags=['Auth'],
        responses={
            200: {
                'description': 'Verification email sent successfully',
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'object',
                            'properties': {
                                'success': {'type': 'boolean'},
                                'message': {'type': 'string'}
                            }
                        }
                    }
                }
            },
            400: {
                'description': 'User not found or already verified',
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'object',
                            'properties': {
                                'success': {'type': 'boolean'},
                                'message': {'type': 'string'},
                                'error': {'type': 'string'}
                            }
                        }
                    }
                }
            }
        }
    )
    def post(self, request):
        """
        Resend verification email
        """
        email = request.data.get('email')
        
        if not email:
            return self.error_response(
                message="Email address is required",
                error="MISSING_EMAIL",
                status_code=400
            )
        
        try:
            user = User.objects.get(email=email)
            
            # Check if already verified
            if user.is_email_verified:
                return self.error_response(
                    message="Email is already verified",
                    error="ALREADY_VERIFIED",
                    status_code=400
                )
            
            # Import here to avoid circular imports
            from notification.tasks import send_email_verification
            
            # Queue the email verification task
            send_email_verification.delay(user.id)
            
            return self.success_response(
                data=None,
                message="Verification email sent successfully"
            )
            
        except User.DoesNotExist:
            return self.error_response(
                message="User with this email address not found",
                error="USER_NOT_FOUND",
                status_code=400
            )
        except Exception as e:
            logger.error(f"Error resending verification email: {str(e)}")
            return self.error_response(
                message="An error occurred while sending verification email",
                error="SEND_ERROR",
                status_code=500
            )
