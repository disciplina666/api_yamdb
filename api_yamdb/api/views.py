import random

from django.conf import settings
from django.core.mail import send_mail
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User

from .serializers import CodeAuthSerializer, UserSerializer


class CodeAuthView(APIView):
    def post(self, request):
        serializer = CodeAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })

class CodeViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=['post'])
    def send_code(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        username = serializer.validated_data['username']

        code = ''.join(random.choices('0123456789', k=8))

        user, created = User.objects.get_or_create(
            email=email,
            defaults={'username': username, 'confirmation_code': code}
        )

        if not created:
            user.confirmation_code = code
            user.save()

        send_mail(
            subject='Ваш код подтверждения',
            message=f'Код для входа: {code}',
            from_email='<EMAIL>',
            recipient_list=[email],
            fail_silently=False,
        )

        return Response(
            {'email': email, 'username': username},
            status=status.HTTP_200_OK
        )