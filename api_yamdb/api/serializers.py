from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from reviews.constants import EMAIL_MAX_LENGTH, USERNAME_MAX_LENGTH
from reviews.models import Category, Comment, Genre, Review, Title, User
from reviews.validators import validate_username, validate_year


class UserSerializer(serializers.ModelSerializer):

    def validate_username(self, username):
        return validate_username(username)

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
        max_length=USERNAME_MAX_LENGTH,
        required=True,
    )
    email = serializers.EmailField(
        max_length=EMAIL_MAX_LENGTH,
        required=True,
    )

    def validate_username(self, username):
        return validate_username(username)


class TokenObtainSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=USERNAME_MAX_LENGTH,
        required=True,
    )
    confirmation_code = serializers.CharField(
        max_length=settings.CONFIRMATION_CODE_MAX_LENGTH,
        required=True,
    )

    def validate_username(self, username):
        return validate_username(username)


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
        fields = read_only_fields = (
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
        return validate_year(value)

    def to_representation(self, title):
        return TitleReadSerializer(title).data


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
        if (
            (request := self.context['request']).method == 'POST'
            and Review.objects.filter(
                author=request.user,
                title=self.context['view'].get_title()
            ).exists()
        ):
            raise ValidationError(
                'Вы уже оставляли отзыв к этому произведению.')
        return data


class CommentSerializer(BaseAuthorSerializer):
    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
