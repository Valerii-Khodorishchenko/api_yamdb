import random

from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters import rest_framework
from rest_framework import filters, mixins, status, views, viewsets
from rest_framework.decorators import action
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
from api_yamdb.constants import RESERVED_NAME
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
    length = settings.CONFIRMATION_CODE_MAX_LENGTH
    allowed_chars = settings.CONFIRMATION_CODE_CHARS
    return ''.join(random.choices(allowed_chars, k=length))


class SignUpView(views.APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = UserSignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        email = serializer.validated_data['email']
        user = User.objects.filter(username=username).first()
        if user:
            if user.email != email:
                return Response(
                    {'email': ['Email не совпадает.']},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            if User.objects.filter(email=email).exists():
                return Response(
                    {'email': ['Пользователь с таким email уже существует.']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user = User.objects.create_user(username=username, email=email)
        confirmation_code = get_random_code()
        user.confirmation_code = confirmation_code
        user.save()
        send_confirmation_code(user, confirmation_code)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenView(views.APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = TokenObtainSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        confirmation_code = serializer.validated_data['confirmation_code']
        user = get_object_or_404(
            User, username=serializer.validated_data['username'])
        if user.confirmation_code != confirmation_code:
            return Response(
                {'confirmation_code': ['Неверный код подтверждения.']},
                status=status.HTTP_400_BAD_REQUEST
            )
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
        serializer_class=CurrentUserSerializer
    )
    def get_current_user(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        elif request.method == 'PATCH':
            serializer = self.get_serializer(
                request.user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class CategoryGenreMixin(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = (IsAdminOrReadOnly,)


class CategoryViewSet(CategoryGenreMixin):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CategoryGenreMixin):
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
