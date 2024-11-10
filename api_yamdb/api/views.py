import random

from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.db.utils import IntegrityError
from django_filters import rest_framework
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.permissions import (
    AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly)
from rest_framework_simplejwt.tokens import AccessToken

from api.serializers import (
    CategorySerializer,
    CommentSerializer,
    CurrentUserSerializer,
    GenreSerializer,
    ReviewSerializer,
    TokenObtainSerializer,
    TitleReadSerializer,
    TitleWriteSerializer,
    UserSerializer,
    UserSignUpSerializer
)
from api.permissions import (
    IsAdmin, IsAdminOrReadOnly, IsAuthorOrModeratorOrAdmin)
from reviews.models import Category, Genre, Review, Title, User


def send_confirmation_code(user, confirmation_code):
    send_mail(
        'Код подтверждения',
        f'Ваш код подтверждения: {confirmation_code}',
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False
    )


def get_random_code():
    return ''.join(random.choices(
        settings.CONFIRMATION_CODE_CHARS,
        k=settings.CONFIRMATION_CODE_MAX_LENGTH
    ))


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = UserSignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data['username']
    email = serializer.validated_data['email']
    try:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': email}
        )
        if not created and user.email != email:
            raise ValidationError({'email': 'Email не совпадает.'})
    except IntegrityError:
        raise ValidationError(
            {'email': 'Пользователь с таким email уже зарегистрирован.'})
    else:
        confirmation_code = get_random_code()
        user.confirmation_code = confirmation_code
        user.save()
        send_confirmation_code(user, confirmation_code)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def token_obtain(request):
    serializer = TokenObtainSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    confirmation_code = serializer.validated_data['confirmation_code']
    user = get_object_or_404(
        User, username=serializer.validated_data['username'])
    if user.confirmation_code != confirmation_code:
        raise ValidationError(
            {'confirmation_code': 'Неверный код подтверждения.'})
    user.confirmation_code = ''
    user.save()
    return Response(
        {'token': str(AccessToken.for_user(user))},
        status=status.HTTP_200_OK
    )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    http_method_names = ('get', 'post', 'patch', 'delete')

    @action(
        detail=False,
        methods=('get', 'patch'),
        permission_classes=(IsAuthenticated,),
        url_path=settings.RESERVED_NAME,
    )
    def user_profile(self, request):
        if request.method == 'GET':
            return Response(UserSerializer(request.user).data)
        serializer = CurrentUserSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class AdminCreateDestroySlugViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet

):
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = (IsAdminOrReadOnly,)


class CategoryViewSet(AdminCreateDestroySlugViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(AdminCreateDestroySlugViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleFilter(rest_framework.FilterSet):
    category = rest_framework.CharFilter(field_name='category__slug')
    genre = rest_framework.CharFilter(field_name='genre__slug')

    class Meta:
        model = Title
        fields = ('category', 'genre', 'name', 'year')


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).order_by(*Title._meta.ordering)
    filter_backends = (rest_framework.DjangoFilterBackend,)
    filterset_class = TitleFilter
    permission_classes = (IsAdminOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly, IsAuthorOrModeratorOrAdmin,)
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs['title_id'])

    def get_queryset(self):
        return self.get_title().reviews.select_related('title')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly, IsAuthorOrModeratorOrAdmin,)
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_review(self):
        return get_object_or_404(Review, id=self.kwargs['review_id'])

    def get_queryset(self):
        return self.get_review().comments.select_related('review')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
