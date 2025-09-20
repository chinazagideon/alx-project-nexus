"""
User serializers
"""
from rest_framework import serializers
from .models.models import User
from .models.models import UserRole

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the user model
    """
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'role',
            'phone',
            'status',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('created_at', 'updated_at', 'id')
        required_fields = ('username', 'email', 'first_name', 'last_name', 'phone')

    def validate(self, attrs):
        """
        Validate the user data
        """

        # check if the username is already taken
        if User.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError("Username already taken")

        # check if the email is already taken
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError("Email already taken")

        # check if the phone is already taken
        if User.objects.filter(phone=attrs['phone']).exists():
            raise serializers.ValidationError("Phone already taken")

        # check if the role is valid
        if attrs['role'] not in UserRole.values:
            raise serializers.ValidationError("Invalid role")

        return attrs
        
    def create(self, validated_data):
        """
        Create a new user
        """
        return User.objects.create_user(**validated_data)
    