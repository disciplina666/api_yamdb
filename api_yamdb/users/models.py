from django.db import models
from django.contrib.auth.models import AbstractUser

from .constants import (
    MAX_LENGTH150, MAX_LENGTH20, MAX_LENGTH254
)


class User(AbstractUser):
    """Пользователь с дополнительными полями."""

    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    ROLE_CHOICES = [
        (USER, 'Пользователь'),
        (MODERATOR, 'Модератор'),
        (ADMIN, 'Администратор'),
    ]

    first_name = models.CharField(
        'имя',
        max_length=MAX_LENGTH150,
        default='',
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=MAX_LENGTH150,
        default='',
    )

    bio = models.TextField(
        'Биография',
        blank=True,
        null='',
    )
    role = models.CharField(
        'Роль',
        max_length=MAX_LENGTH20,
        choices=ROLE_CHOICES,
        default=USER,
    )
    email = models.EmailField(
        'Email',
        max_length=MAX_LENGTH254,
        unique=True,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR
