from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from .views import (CategoryViewSet,
                    GenreViewSet,
                    TitleViewSet,
                    CodeAuthView,
                    CodeViewSet,
                    UserViewSet,
                    )

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('genres', GenreViewSet, basename='genre')
router.register('titles', TitleViewSet, basename='title')
router.register('users', UserViewSet)

urlpatterns = [
    path('auth/signup/',
         CodeViewSet.as_view({'post': 'send_code'}),
         name='send_code'),
    path('', include(router.urls)),
    path('auth/token/', CodeAuthView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
