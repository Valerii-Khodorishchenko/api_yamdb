"""Users serializers."""
from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    """User serializer."""

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )


class UserSignUpSerializer(serializers.ModelSerializer):
    """User sign up serializer."""

    class Meta:
        model = User
        fields = ('email', 'username')
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
        }

    def validate_username(self, value):
        """Validate username."""
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Использование "me" в качестве имени пользователя запрещено.'
            )
        return value

    def validate(self, data):
        """Validate user data."""
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError(
                'Пользователь с таким именем уже существует.'
            )
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError(
                'Пользователь с таким email уже существует.'
            )
        return data
