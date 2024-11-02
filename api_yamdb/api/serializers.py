from rest_framework import serializers
from rest_framework.exceptions import NotFound
from django.contrib.auth.tokens import default_token_generator as dtg
from django.contrib.auth.validators import UnicodeUsernameValidator

from reviews.models import User


class UserSerializer(serializers.ModelSerializer):
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
    username = serializers.CharField(
        max_length=150,
        required=True,
        validators=[UnicodeUsernameValidator()],
    )
    email = serializers.EmailField(max_length=254, required=True)
    class Meta:
        model = User
        fields = ('email', 'username')

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Использование "me" в качестве имени пользователя запрещено.'
            )
        return value


class TokenObtainSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get('username')
        confirmation_code = attrs.get('confirmation_code')
        user = User.objects.filter(username=username).first()
        if user is None:
            raise NotFound(
                'Пользователь с таким именем не существует.'
            )
        if not dtg.check_token(user, confirmation_code):
            raise serializers.ValidationError(
                'Неверный код подтверждения.'
            )
        attrs['user'] = user
        return attrs


class CurrentUserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(read_only=True)
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
