import datetime

from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator

from reviews.models import Category, Comment, Genre, Review, Title, User
from reviews.validators import validate_username


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=settings.USERNAME_MAX_LENGTH,
        validators=[
            validate_username,
            UniqueValidator(
                queryset=User.objects.all(),
                message='Пользователь с таким именем уже существует.'
            )
        ],
        required=True,
    )
    email = serializers.EmailField(
        max_length=settings.EMAIL_MAX_LENGTH,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message='Пользователь с таким email уже существует.'
            )
        ],
        required=True,
    )

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
        max_length=settings.USERNAME_MAX_LENGTH,
        required=True,
        validators=[validate_username],
    )
    email = serializers.EmailField(
        max_length=settings.EMAIL_MAX_LENGTH,
        required=True
    )


class TokenObtainSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=settings.USERNAME_MAX_LENGTH,
        required=True,
    )
    confirmation_code = serializers.CharField(
        max_length=settings.CONFIRMATION_CODE_MAX_LENGTH,
        required=True,
    )


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleReadSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )


class TitleWriteSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'description', 'genre', 'category'
        )

    def validate_year(self, value):
        current_year = datetime.date.today().year
        if value > current_year:
            raise serializers.ValidationError(
                'Год выпуска ({value}) не может быть больше '
                'текущего года ({current_year}).'
            )
        return value


class BaseAuthorSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    class Meta:
        abstract = True


class ReviewSerializer(BaseAuthorSerializer):
    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, data):
        if (request := self.context['request']) and request.method == 'POST':
            if Review.objects.filter(
                author=request.user,
                title=self.context['view'].get_title()
            ).exists():
                raise ValidationError(
                    'Вы уже оставляли отзыв к этому произведению.')
        return data


class CommentSerializer(BaseAuthorSerializer):
    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
