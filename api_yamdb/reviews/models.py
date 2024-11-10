from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from reviews.constants import (
    EMAIL_MAX_LENGTH,
    USERNAME_MAX_LENGTH,
    DESCRIPTION_LENGTH,
    SLUG_MAX_LENGTH,
    NAME_MAX_LENGTH,
    SCORE
)
from reviews.validators import validate_username, validate_year


class User(AbstractUser):
    class Role(models.TextChoices):
        USER = 'user', 'Пользователь'
        MODERATOR = 'moderator', 'Модератор'
        ADMIN = 'admin', 'Администратор'

    bio = models.TextField('О себе', blank=True)
    role = models.CharField(
        'Роль',
        max_length=max(len(role.value) for role in Role),
        choices=Role.choices,
        default=Role.USER,
    )
    email = models.EmailField(
        'Адрес электронной почты',
        max_length=EMAIL_MAX_LENGTH,
        unique=True
    )
    username = models.CharField(
        'Никнейм',
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
        help_text=(
            'Укажите пользователя.',
        ),
        validators=[validate_username],
    )
    confirmation_code = models.CharField(
        'Код подтверждения',

        max_length=settings.CONFIRMATION_CODE_MAX_LENGTH,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username[:DESCRIPTION_LENGTH]

    @property
    def is_admin(self):
        return (
            self.role == self.Role.ADMIN or self.is_staff
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
        return self.name[:DESCRIPTION_LENGTH]


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
        return self.name[:DESCRIPTION_LENGTH]


class BaseContentModel(models.Model):
    text = models.TextField('Текст')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,

        verbose_name='Автор'
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ('-pub_date',)
        default_related_name = '%(class)ss'

    def __str__(self):
        return (f'{self.__class__.__name__}'
                f' от {self.author}')


class Review(BaseContentModel):
    score = models.PositiveSmallIntegerField(
        'Оценка',
        validators=[
            MinValueValidator(SCORE['min'], message=SCORE['message']),
            MaxValueValidator(SCORE['max'], message=SCORE['message'])
        ]
    )
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE,
        verbose_name='Произведение',
    )

    class Meta(BaseContentModel.Meta):
        verbose_name = 'отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_review'
            )
        ]

    def __str__(self):
        return f'Отзыв от {self.author} на {self.title}'[:DESCRIPTION_LENGTH]


class Comment(BaseContentModel):
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE,
        verbose_name='Отзыв',
    )

    class Meta(BaseContentModel.Meta):
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return (f'{self.author} '
                f'прокомментировал {self.review}')
