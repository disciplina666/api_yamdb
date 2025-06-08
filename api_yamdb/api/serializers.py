from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User


class CodeAuthSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    def validate(self, data):
        username = data.get('username')
        confirmation_code = data.get('confirmation_code')

        user = get_object_or_404(User, username=username)
        if not default_token_generator.check_token(user, confirmation_code):
            raise serializers.ValidationError(
                {'confirmation_code': 'Неверный код подтверждения'}
            )

        data['user'] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
        extra_kwargs = {
            'username': {
                'required': True,
                'help_text': 'Только буквы, цифры и @/./+/-/_'
            },
            'email': {
                'required': True,
                'help_text': 'Максимальная длина 254 символа'
            }
        }


class SignUpSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ('email', 'username',)
        extra_kwargs = {
            'username': {
                'required': True,
                'help_text': 'Только буквы, цифры и @/./+/-/_'
            },
            'email': {
                'required': True,
                'help_text': 'Максимальная длина 254 символа'
            }
        }


class UserRoleSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        read_only_fields = ('role',)

    def validate(self, data):
        for attr, value in data.items():
            setattr(self.instance, attr, value)
        try:
            self.instance.full_clean()
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)
        return data


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class GenreTitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(slug_field='slug', read_only=True)
    title = serializers.SlugRelatedField(slug_field='name', read_only=True)

    class Meta:
        model = Title
        fields = ('id', 'genre', 'title')


class TitleReadSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'description', 'genre', 'category', 'rating'
        )


class TitleWriteSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        many=True, slug_field='slug', queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        read_only_fields = ('author', 'pub_date')

    def create(self, validated_data):
        validated_data.pop('author', None)

        return Review.objects.create(
            title=self.context['title'],
            author=self.context['request'].user,
            **validated_data
        )


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
        read_only_fields = ('author', 'pub_date')
