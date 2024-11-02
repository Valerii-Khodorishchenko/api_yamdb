from django.core.validators import (
    MaxValueValidator, MinValueValidator, EmailValidator
)
from django.db import models
<<<<<<< HEAD
from django.db.models import Avg
#TODO удалить после сздания кастомной модели User
from django.contrib.auth import get_user_model
=======
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
>>>>>>> 651b5ae721ac6a5dff7af52c3ac5a10dcb28a752



class Category(models.Model):
    name = models.CharField('Название категории', max_length=256)
    slug = models.SlugField(
        'Идентификатор категории',
        max_length=50,
        unique=True
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name[:26]


class User(AbstractUser):
    class Role(models.TextChoices):
        USER = 'user', 'User'
        MODERATOR = 'moderator', 'Moderator'
        ADMIN = 'admin', 'Admin'

    bio = models.TextField('О себе', blank=True)
    role = models.CharField(
        'Роль',
        max_length=10,
        choices=Role.choices,
        default=Role.USER,
    )
    email = models.EmailField(
        'Адрес электронной почты',
        max_length=254,
        unique=True,
        validators=(EmailValidator(),),
    )
    username = models.CharField(
        'Имя пользователя',
        max_length=150,
        unique=True,
        help_text=(
            'Не более 150 символов. Только буквы, цифры и @/./+/-/_.',
        ),
        validators=(UnicodeUsernameValidator(),),
        error_messages={
            'unique': 'Пользователь с таким username уже существует.',
        },
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
            self.role == self.Role.ADMIN or self.is_superuser
        )

    @property
    def is_moderator(self):
        return self.role == self.Role.MODERATOR

class Genre(models.Model):
    name = models.CharField('Название жанра', max_length=256)
    slug = models.SlugField(
        'Идентификатор жанра',
        max_length=50,
        unique=True
    )

    class Meta:
        verbose_name = 'жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name[:26]


class Title(models.Model):
    name = models.CharField('Название произведения', max_length=256)
    year = models.PositiveIntegerField('Год')
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        null=True, verbose_name='Категория'
    )
    genre = models.ManyToManyField(Genre, verbose_name='Жанр')
    rating = models.DecimalField(
        'Средний рейтинг', max_digits=3, decimal_places=1,
        null=True, blank=True
    )

    class Meta:
        verbose_name = 'произведение'
        verbose_name_plural = 'Произведения'
        default_related_name = 'titles'

    def __str__(self):
        return self.name[:26]

    def update_rating(self):
        average_score = self.reviews.aggregate(Avg('score'))['score__avg']
        self.rating = round(average_score, 1) if average_score is not None else None
        self.save()


class Review(models.Model):
    text = models.TextField('Текст отзыва')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Автор отзыва'
    )
    score = models.PositiveSmallIntegerField(
        'Рейтинг',
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE,
        verbose_name='Произведение'
    )

    class Meta:
        verbose_name = 'отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ('-pub_date',)
        default_related_name = 'reviews'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_author_title'
            )
        ]

    def __str__(self):
        return f'Отзыв от {self.author} на {self.title}'


class Comment(models.Model):
    text = models.TextField('Текст комментария')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Автор комментария'
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE,
        verbose_name='Отзыв'
    )

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-pub_date',)
        default_related_name = 'comments'

    def __str__(self):
        return f'{self.author} прокомментировал {self.review}'

