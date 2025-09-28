"""
User serializers
"""

from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from .models.models import User, UserRole


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the user model
    """

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "password",
            "phone",
            "status",
            "is_email_verified",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at", "id", "is_email_verified")
        required_fields = ("username", "email", "first_name", "last_name", "phone", "password")
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def validate(self, attrs):
        """
        Validate the user data
        """
        # Check if the username is already taken
        if User.objects.filter(username=attrs["username"]).exists():
            raise serializers.ValidationError("Username already taken")

        # Check if the email is already taken
        if User.objects.filter(email=attrs["email"]).exists():
            raise serializers.ValidationError("Email already taken")

        # Check if the phone is already taken (only if phone is provided)
        if attrs.get("phone") and User.objects.filter(phone=attrs["phone"]).exists():
            raise serializers.ValidationError("Phone already taken")

        # Check if the password is valid
        if len(attrs["password"]) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long")

        # Check if the role is valid and restrict admin role
        allowed_roles = [UserRole.TALENT, UserRole.RECRUITER]
        if attrs["role"] not in allowed_roles:
            raise serializers.ValidationError("Invalid role. Only 'talent' and 'recruiter' roles are allowed.")

        return attrs

    def create(self, validated_data):
        """
        Create a new user with hashed password
        """
        # Hash the password before saving
        password = validated_data.pop("password")
        user = User.objects.create(**validated_data)
        user.set_password(password)  # This properly hashes the password
        user.save()
        return user

    def update(self, instance, validated_data):
        """
        Update user with hashed password if provided
        """
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)  # Hash the new password
            user.save()

        return user


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration with password confirmation
    """

    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "phone",
            "password",
            "password_confirm",
        )
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def validate(self, attrs):
        """
        Validate the registration data
        """
        # Check if passwords match
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError("Passwords do not match")

        # Check if the username is already taken
        if User.objects.filter(username=attrs["username"]).exists():
            raise serializers.ValidationError("Username already taken")

        # Check if the email is already taken
        if User.objects.filter(email=attrs["email"]).exists():
            raise serializers.ValidationError("Email already taken")

        # Check if the phone is already taken (only if phone is provided)
        if attrs.get("phone") and User.objects.filter(phone=attrs["phone"]).exists():
            raise serializers.ValidationError("Phone already taken")

        # Check if the password is valid
        if len(attrs["password"]) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long")

        # Restrict role selection - only allow talent and recruiter for public registration
        allowed_roles = [UserRole.TALENT, UserRole.RECRUITER]
        if attrs["role"] not in allowed_roles:
            raise serializers.ValidationError(
                "Invalid role. Only 'talent' and 'recruiter' roles are allowed for registration."
            )

        return attrs

    def create(self, validated_data):
        """
        Create a new user with hashed password
        """
        # Remove password_confirm from validated_data
        validated_data.pop("password_confirm")

        # Hash the password before saving
        password = validated_data.pop("password")
        user = User.objects.create(**validated_data)
        user.set_password(password)  # This properly hashes the password
        user.save()
        return user
