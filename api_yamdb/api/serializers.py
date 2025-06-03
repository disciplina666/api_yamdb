from django.core.validators import RegexValidator

from rest_framework import exceptions, serializers

from reviews.models import Category, Genre, GenreTitle, Title

from users.models import User


class CodeAuthSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()

    def validate(self, attrs):
        try:
            user = User.objects.get(username=attrs['username'])
            if user.confirmation_code != attrs['confirmation_code']:
                raise exceptions.ValidationError('Неверный код подтверждения')
            return {'user': user}
        except User.DoesNotExist:
            raise exceptions.NotFound('Пользователь не найден')


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True,
        max_length=150,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message='Имя пользователя содержит недопустимые символы',
                code='invalid_username'
            )
        ]
    )
    email = serializers.EmailField(required=True, max_length=254)

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )

    def validate(self, data):
        email = data.get('email')
        username = data.get('username')

        if username:
            if username.lower() == 'me':
                raise serializers.ValidationError(
                    {'username': 'Имя пользователя "me" не разрешено'}
                )
        if username and email:
            try:
                user = User.objects.get(username=username)
                if user.email != email:
                    raise serializers.ValidationError(
                        {'email': (
                            'Этот username уже зарегистрирован c другим email'
                        )}
                    )
            except User.DoesNotExist:
                if User.objects.filter(email=email).exists():
                    raise serializers.ValidationError(
                        {'email': 'Этот email уже зарегистрирован'}
                    )

        return data


class UserRoleSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        read_only_fields = (
            'role', 'username', 'email', 'is_superuser', 'is_staff'
        )


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
        model = GenreTitle
        fields = ('id', 'genre', 'title')


class TitleReadSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'description',
            'genre', 'category', 'rating'
        )


class TitleWriteSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = (
            'name', 'year', 'description',
            'genre', 'category'
        )

    def create(self, validated_data):
        genres = validated_data.pop('genre')
        title = Title.objects.create(**validated_data)
        for genre in genres:
            GenreTitle.objects.create(genre=genre, title=title)
        return title

    def update(self, instance, validated_data):
        genres = validated_data.pop('genre', None)
        if genres is not None:
            instance.genre.clear()
            for genre in genres:
                GenreTitle.objects.create(genre=genre, title=instance)
        return super().update(instance, validated_data)
