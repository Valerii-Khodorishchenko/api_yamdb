from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.validators import UnicodeUsernameValidator


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
    email = models.EmailField('Email', unique=True)

    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        'Username',
        max_length=150,
        unique=True,
        help_text=(
            'Не более 150 символов. Только буквы, цифры и @/./+/-/_.',
        ),
        validators=[username_validator],
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
