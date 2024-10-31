"""Users urls."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, SignupView, TokenObtainView, MeView


router = DefaultRouter()
router.register('users', UserViewSet, basename='users')


urlpatterns = [
    path('', include(router.urls)),
    path('auth/signup/', SignupView.as_view(), name='signup'),
    path('auth/token/', TokenObtainView.as_view(), name='token_obtain'),
    path('me/', MeView.as_view(), name='me'),
]
