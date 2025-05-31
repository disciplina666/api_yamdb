from django.contrib.auth import authenticate, get_user_model
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions, serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

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
        fields = ('username', 'email')

    def validate(self, data):
        email = data.get('email')
        username = data.get('username')

        if username.lower() == 'me':
            raise serializers.ValidationError(
                {'username': 'Имя пользователя "me" не разрешено'}
            )

        try:
            user = User.objects.get(username=username)
            if user.email != email:
                raise serializers.ValidationError(
                    {'email': 'Этот username уже зарегистрирован с другим email'}
                )
        except User.DoesNotExist:
            if User.objects.filter(email=email).exists():
                raise serializers.ValidationError(
                    {'email': 'Этот email уже зарегистрирован'}
                )

        return data