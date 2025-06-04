import random

from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import Category, Genre, Title
from users.models import User

from .permissions import IsAdmin, IsAdminOrReadOnly
from .serializers import (
    CategorySerializer,
    CodeAuthSerializer,
    GenreSerializer,
    TitleReadSerializer,
    TitleWriteSerializer,
    UserRoleSerializer,
    UserSerializer,
)
from .filters import TitleFilter


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    filter_backends = [filters.SearchFilter]
    search_fields = ['username']
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    @action(
        detail=False,
        methods=['get', 'patch'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        user = self.request.user

        serializer_class = UserRoleSerializer

        if request.method == 'GET':
            serializer = serializer_class(user)
            return Response(serializer.data)

        if self.request.method == 'PATCH':
            serializer = serializer_class(
                user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response(serializer.data)


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


class CategoryViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    pagination_class = PageNumberPagination


class GenreViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_field = 'slug'
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    pagination_class = PageNumberPagination


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).all()
    permission_classes = [IsAdminOrReadOnly]
    # filter_backends = [filters.SearchFilter]
    # filterset_fields = ['category__slug', 'genre__slug', 'name', 'year']
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TitleReadSerializer
        return TitleWriteSerializer
