"""Users models."""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """User model."""

    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    ROLE_CHOICES = (
        (USER, 'user'),
        (MODERATOR, 'moderator'),
        (ADMIN, 'admin'),
    )
    bio = models.TextField('О себе', blank=True)
    role = models.CharField(
        'Роль',
        max_length=20,
        choices=ROLE_CHOICES,
        default='user'
    )

    @property
    def is_admin(self):
        """Is admin."""
        return (
            self.role == self.ADMIN or self.is_superuser
        )

    @property
    def is_moderator(self):
        """Is moderator."""
        return self.role == self.MODERATOR
