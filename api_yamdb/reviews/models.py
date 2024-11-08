from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from api.validators import validate_username, validate_year
from api_yamdb.constants import (
    CONFIRMATION_CODE_MAX_LENGTH,
    EMAIL_MAX_LENGTH,
    NAME_MAX_LENGTH,
    SCORE,
    SLUG_MAX_LENGTH,
    USERNAME_MAX_LENGTH,
)


class User(AbstractUser):
    class Role(models.TextChoices):
        USER = 'user', 'Пользователь'
        MODERATOR = 'moderator', 'Модератор'
        ADMIN = 'admin', 'Администратор'

    bio = models.TextField('О себе', blank=True)
    max_role_length = max(len(role.value) for role in Role)
    role = models.CharField(
        'Роль',
        max_length=max_role_length,
        choices=Role.choices,
        default=Role.USER,
    )
    email = models.EmailField(
        'Адрес электронной почты',
        max_length=EMAIL_MAX_LENGTH,
        unique=True,
    )
    username = models.CharField(
        'Имя пользователя',
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
        help_text=(
            'Только буквы, цифры и @/./+/-/_.',
        ),
        validators=[validate_username],
    )
    confirmation_code = models.CharField(
        'Код подтверждения',
        max_length=CONFIRMATION_CODE_MAX_LENGTH,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return (

            self.role == self.Role.ADMIN or self.is_staff or self.is_superuser
        )

    @property
    def is_moderator(self):
        return self.role == self.Role.MODERATOR


class BaseNameSlugModel(models.Model):
    name = models.CharField('Название', max_length=NAME_MAX_LENGTH)
    slug = models.SlugField(
        'Идентификатор',
        max_length=SLUG_MAX_LENGTH,
        unique=True
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.name[:26]


class Category(BaseNameSlugModel):
    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'


class Genre(BaseNameSlugModel):
    class Meta:
        verbose_name = 'жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    name = models.CharField('Название', max_length=NAME_MAX_LENGTH)
    year = models.PositiveIntegerField(
        'Год выпуска', validators=[validate_year]
    )
    description = models.TextField(
        'Описание',
        null=True
    )
    genre = models.ManyToManyField(Genre, verbose_name='Жанры')
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        null=True, verbose_name='Категория'
    )

    class Meta:
        ordering = ('-year', 'name')
        verbose_name = 'произведение'
        verbose_name_plural = 'Произведения'
        default_related_name = 'titles'

    def __str__(self):
        return self.name[:26]


class BaseContentReviewComment(models.Model):
    text = models.TextField('Текст')
    author = models.ForeignKey(
        'User', on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ('-pub_date',)


class Review(BaseContentReviewComment):
    score = models.PositiveSmallIntegerField(
        'Рейтинг',
        validators=[
            MinValueValidator(SCORE['min'], message=SCORE['message']),
            MaxValueValidator(SCORE['max'], message=SCORE['message'])
        ]
    )
    title = models.ForeignKey(
        'Title', on_delete=models.CASCADE,
        verbose_name='Произведение'
    )

    class Meta(BaseContentReviewComment.Meta):
        verbose_name = 'отзыв'
        verbose_name_plural = 'Отзывы'
        default_related_name = 'reviews'
        unique_together = ('author', 'title')

    def __str__(self):
        return f'Отзыв от {self.author} на {self.title}'


class Comment(BaseContentReviewComment):
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE,
        verbose_name='Отзыв'
    )

    class Meta(BaseContentReviewComment.Meta):
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        default_related_name = 'comments'

    def __str__(self):
        return f'{self.author} прокомментировал {self.review}'
