from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone as datezone

from .constants import MAX_LENGTH_NAME, MAX_LENGTH_SLUG

User = get_user_model()


def validate_year(value):
    current_year = datezone.now().year
    if value > current_year:
        raise ValidationError('Год не может быть больше текущего.')


class Category(models.Model):
    name = models.CharField(
        max_length=MAX_LENGTH_NAME, verbose_name='Категория'
    )
    slug = models.SlugField(
        max_length=MAX_LENGTH_SLUG, unique=True, verbose_name='Слаг(ссылка)'
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=MAX_LENGTH_NAME, verbose_name='Жанр')
    slug = models.SlugField(
        max_length=MAX_LENGTH_SLUG, unique=True, verbose_name='Слаг(ссылка)'
    )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ['name']

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        max_length=MAX_LENGTH_NAME, verbose_name='Название'
    )
    year = models.PositiveSmallIntegerField(
        'Год',
        validators=[
            MinValueValidator(1800),
        ]
    )
    description = models.TextField('Описание', blank=True)
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        verbose_name='Жанр'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles',
        verbose_name='Категории'
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ['name']

    def __str__(self):
        return self.name


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Заголовок',
        related_name='reviews'
    )
    text = models.TextField('Текст')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор'
    )
    score = models.PositiveSmallIntegerField(
        'Балл', validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-pub_date']
        unique_together = ('title', 'author')

    def __str__(self):
        return f'{self.author} - {self.title} ({self.score})'


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='комментарий',
        related_name='comments'
    )
    text = models.TextField('Текст')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-pub_date']

    def __str__(self):
        return f'Комментарий от {self.author} к отзыву {self.review_id}'
