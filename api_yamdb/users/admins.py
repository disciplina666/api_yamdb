from django.contrib import admin
from .models import User
from reviews.models import Category, Genre, Title, Review, Comment, GenreTitle


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        'role',
        'first_name',
        'last_name',
        'is_staff',
    )
    list_editable = ('role',)
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('role', 'is_staff', 'is_superuser')
    empty_value_display = 'пусто'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    empty_value_display = 'пусто'


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    empty_value_display = 'пусто'


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'year',
        'category',
        'display_genres',
        'description',
    )
    search_fields = ('name', 'category__name', 'genre__name')
    list_filter = ('year', 'category', 'genre')
    filter_horizontal = ('genre',)
    empty_value_display = 'пусто'

    def display_genres(self, obj):
        return ", ".join([genre.name for genre in obj.genre.all()])
    display_genres.short_description = 'Жанры'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'text',
        'score',
        'author',
        'title',
        'pub_date',
    )
    search_fields = ('text', 'author__username', 'title__name')
    list_filter = ('score', 'pub_date')
    empty_value_display = 'пусто'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'text',
        'author',
        'review',
        'pub_date',
    )
    search_fields = ('text', 'author__username')
    list_filter = ('pub_date',)
    empty_value_display = 'пусто'


@admin.register(GenreTitle)
class GenreTitleAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'genre',
    )
    search_fields = ('title__name', 'genre__name')
    list_filter = ('genre',)
    empty_value_display = 'пусто'
