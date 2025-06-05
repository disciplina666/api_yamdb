from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from .views import (
    CategoryViewSet,
    CodeAuthView,
    CodeViewSet,
    GenreViewSet,
    TitleViewSet,
    UserViewSet,
    ReviewViewSet,
    CommentViewSet,
)

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('genres', GenreViewSet, basename='genre')
router.register('titles', TitleViewSet, basename='title')
router.register('users', UserViewSet, basename='user')

router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)

urlpatterns = [
    path('auth/signup/', CodeViewSet.as_view({'post': 'send_code'}),
         name='send_code'),
    path('auth/token/', CodeAuthView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(),
         name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('', include(router.urls)),
]
