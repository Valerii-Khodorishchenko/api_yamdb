from django.db import models


class Category(models.Model):
    name = models.CharField('Название категории', max_length=256)
    slug = models.SlugField('Идентификатор категории', unique=True)

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name[:26]


class Genre(models.Model):
    name = models.CharField('Название жанра', max_length=256)
    slug = models.SlugField('Идентификатор жанра', unique=True)

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
