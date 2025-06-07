from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxLengthValidator, RegexValidator
from django.db import models

from users.validators import validate_username

from .constants import MAX_LENGTH_EMAIL, MAX_LENGTH_NAME, MAX_LENGTH_ROLE


class User(AbstractUser):
    """Модель пользователя."""

    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    CHOICES = (
        (USER, 'Аутентифицированный пользователь'),
        (MODERATOR, 'Модератор'),
        (ADMIN, 'Админ'),
    )

    role = models.CharField(
        max_length=MAX_LENGTH_ROLE,
        choices=CHOICES,
        default=USER,
        verbose_name='Уровень доступа пользователя',
        help_text='Уровень доступа пользователя'
    )

    bio = models.TextField(
        blank=True,
        verbose_name='Заметка о пользователе',
        help_text='Напишите заметку о себе'
    )

    email = models.EmailField(
        unique=True,
        max_length=MAX_LENGTH_EMAIL,
        validators=[MaxLengthValidator(MAX_LENGTH_EMAIL)],
        verbose_name='Электронная почта пользователя',
        help_text='Введите свой электронный адрес'
    )

    username = models.CharField(
        max_length=MAX_LENGTH_NAME,
        unique=True,
        help_text=(
            'Обязательное поле. 150 символов или меньше. '
            'Только буквы, цифры и @/./+/-/_ символы.'
        ),
        validators=[
            validate_username,
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message=(
                    'Имя пользователя может содержать только '
                    'буквы, цифры и @/./+/-/_ символы.'
                ),
            ),
        ],
        error_messages={
            'unique': 'Пользователь с таким именем уже существует.',
        },
        verbose_name='Имя пользователя',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)
        constraints = (
            models.UniqueConstraint(
                fields=('username', 'email'),
                name='unique_username_email'
            ),
        )

    def __str__(self):
        return self.username

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_staff
