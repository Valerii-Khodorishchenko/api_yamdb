import datetime

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
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
        user_qs = User.objects.filter(username=username)
        if user_qs.exists():
            user = user_qs.first()
            if user.email != email:
                raise serializers.ValidationError(
                    {'email': 'Email не совпадает.'},
                    {'username': 'Пользователь с таким именем существует.'},
                )
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
        attrs['user'] = user
        return attrs


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
