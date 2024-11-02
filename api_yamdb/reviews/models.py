from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
#TODO удалить после сздания кастомной модели User
from django.contrib.auth import get_user_model

User = get_user_model()  #TODO удалить после сздания кастомной модели User

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

    class Meta:
        verbose_name = 'произведение'
        verbose_name_plural = 'Произведения'
        default_related_name = 'titles'

    def __str__(self):
        return self.name[:26]


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
