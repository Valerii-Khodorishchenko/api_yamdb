from rest_framework import serializers
from rest_framework.exceptions import NotFound
from django.contrib.auth.tokens import default_token_generator as dtg
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db.models import Avg

import datetime

from reviews.models import User, Category, Genre, Title


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )

    def validate_year(self, value):
        current_year = datetime.date.today().year
        if value > current_year:
            raise serializers.ValidationError(
                'Год выпуска не может быть больше текущего года.'
            )
        return value

    def validate_name(self, value):
        if len(value) > 256:
            raise serializers.ValidationError(
                'Название не должно быть больше 256 символов.'
            )
        return value

    def get_rating(self, obj):
        average_score = obj.reviews.aggregate(Avg('score'))['score__avg']
        return round(average_score, 1) if average_score else None

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['genre'] = [
            {
                'name': genre.name, 'slug': genre.slug
            } for genre in instance.genre.all()
        ]
        representation['category'] = {
            'name': instance.category.name, 'slug': instance.category.slug
        }
        return representation


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
