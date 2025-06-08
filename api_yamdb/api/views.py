from django.contrib.auth.tokens import default_token_generator
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (
    IsAuthenticated, IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User

from .filters import TitleFilter
from .permissions import (
    IsAdmin, IsAdminModeratorAuthorOrReadOnly, IsAdminOrReadOnly)
from .serializers import (
    CategorySerializer, CodeAuthSerializer,
    CommentSerializer, GenreSerializer, ReviewSerializer, SignUpSerializer,
    TitleReadSerializer, TitleWriteSerializer, UserRoleSerializer,
    UserSerializer,)
from .utils import send_confirmation_code


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
        user = request.user

        if request.method == 'PATCH':
            serializer = UserRoleSerializer(
                instance=user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


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


class SignUpAPIView(APIView):

    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')

        user = User.objects.filter(username=username, email=email).first()

        if user:
            confirmation_code = default_token_generator.make_token(user)
            send_confirmation_code(confirmation_code, user.email)
            return Response(
                {'email': email, 'username': username},
                status=status.HTTP_200_OK,
            )

        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        confirmation_code = default_token_generator.make_token(user)
        send_confirmation_code(confirmation_code, user.email)
        return Response(
            serializer.validated_data,
            status=status.HTTP_200_OK,
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
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).select_related('category').prefetch_related('genre')
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TitleReadSerializer
        return TitleWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsAdminModeratorAuthorOrReadOnly
    ]
    pagination_class = PageNumberPagination
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        return Review.objects.filter(
            title_id=title_id).select_related('author').prefetch_related(
                'comments__author').order_by('-pub_date')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['title'] = get_object_or_404(
            Title, pk=self.kwargs.get('title_id'))
        return context

    def perform_create(self, serializer):
        title = self.get_serializer_context()['title']
        if Review.objects.filter(
                title=title, author=self.request.user).exists():
            raise serializers.ValidationError(
                'Вы уже оставляли отзыв на это произведение.')
        serializer.save()


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsAdminModeratorAuthorOrReadOnly
    ]
    pagination_class = PageNumberPagination
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        title_id = self.kwargs.get('title_id')
        return Comment.objects.filter(
            review_id=review_id, review__title_id=title_id).select_related(
                'author')

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id'),
            title__id=self.kwargs.get('title_id')
        )
        serializer.save(author=self.request.user, review=review)
