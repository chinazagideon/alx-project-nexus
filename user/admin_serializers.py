"""
Admin-only serializers for user management
"""
from rest_framework import serializers
from .models.models import User, UserRole


class AdminUserSerializer(serializers.ModelSerializer):
    """
    Admin-only serializer for user management including admin role assignment
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
            'is_active',
            'is_staff',
            'is_superuser',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('created_at', 'updated_at', 'id')

    def validate(self, attrs):
        """
        Validate the admin user data
        """
        # Check if the username is already taken (for updates)
        if self.instance and User.objects.filter(username=attrs['username']).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError("Username already taken")
        elif not self.instance and User.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError("Username already taken")

        # Check if the email is already taken (for updates)
        if self.instance and User.objects.filter(email=attrs['email']).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError("Email already taken")
        elif not self.instance and User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError("Email already taken")

        # Check if the phone is already taken (for updates)
        if attrs.get('phone'):
            if self.instance and User.objects.filter(phone=attrs['phone']).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("Phone already taken")
            elif not self.instance and User.objects.filter(phone=attrs['phone']).exists():
                raise serializers.ValidationError("Phone already taken")

        # Check if the role is valid (all roles allowed for admin)
        if attrs['role'] not in UserRole.values:
            raise serializers.ValidationError("Invalid role")

        return attrs

    def create(self, validated_data):
        """
        Create a new user (admin can create any role)
        """
        # Hash the password before saving
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data):
        """
        Update user (admin can update any role)
        """
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        
        if password:
            user.set_password(password)
            user.save()
        
        return user


class AdminUserCreateSerializer(AdminUserSerializer):
    """
    Admin serializer for creating users with password
    """
    password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta(AdminUserSerializer.Meta):
        fields = AdminUserSerializer.Meta.fields + ('password',)
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        """
        Create a new user with hashed password
        """
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user
