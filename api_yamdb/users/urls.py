"""Users urls."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, SignupView


router = DefaultRouter()
router.register('users', UserViewSet, basename='users')


urlpatterns = [
    path('', include(router.urls)),
    path('auth/signup/',
         SignupView.as_view(),
         name='signup'
         ),
]
