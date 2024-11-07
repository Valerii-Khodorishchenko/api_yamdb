import datetime

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator
from rest_framework_simplejwt.tokens import AccessToken
from django.db.models import Avg
from django.shortcuts import get_object_or_404

from reviews.models import Category, Comment, Genre, Review, Title, User


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


class CurrentUserSerializer(UserSerializer):

    class Meta(UserSerializer.Meta):
        read_only_fields = ('role',)


class UserSignUpSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=User._meta.get_field('username').max_length,
        required=True,
        validators=User._meta.get_field('username').validators,
    )
    email = serializers.EmailField(
        max_length=User._meta.get_field('email').max_length,
        required=True,
    )

    def validate(self, data):
        username = data['username']
        email = data['email']
        if (
            User.objects.filter(email=email)
            .exclude(username=username)
            .exists()
        ):
            raise serializers.ValidationError(
                {'email': 'Пользователь с таким email уже существует.'}
            )
        return data


class TokenObtainSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=User._meta.get_field('username').max_length,
        required=True,
    )
    confirmation_code = serializers.CharField(
        max_length=User._meta.get_field('confirmation_code').max_length,
        required=True,
    )

    def validate(self, attrs):
        username = attrs.get('username')
        confirmation_code = attrs.get('confirmation_code')
        user = get_object_or_404(User, username=username)
        if user.confirmation_code != confirmation_code:
            raise serializers.ValidationError(
                {'confirmation_code': 'Неверный код подтверждения.'}
            )
        token = AccessToken.for_user(user)
        return {'token': str(token)}


class CategorySerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(
        max_length=50,
        validators=[UniqueValidator(queryset=Category.objects.all())],
        error_messages={
            'unique': "Эта категория уже существует.",
        }
    )

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(
        max_length=50,
        validators=[UniqueValidator(queryset=Genre.objects.all())],
        error_messages={
            'unique': "Этот жанр уже существует.",
        }
    )

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


class ReviewSerializer(serializers.ModelSerializer):
    title = serializers.HiddenField(
        default=TitleSerializer()
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Review
        fields = '__all__'
        # read_only_fields = ('author', 'title', 'pub_date')
        validators = [
            UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=('author', 'title'),
                message='Вы уже оставляли отзыв к этому произведению.'
            )
        ]


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )
    review = serializers.HiddenField(
        default=None
    )

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('author', 'pub_date')
