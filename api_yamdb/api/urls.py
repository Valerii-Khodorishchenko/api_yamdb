from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, AuthViewSet


router_v1 = DefaultRouter()
router_v1.register('users', UserViewSet, basename='users')
router_v1.register('auth', AuthViewSet, basename='auth')


urlpatterns = [
    path('v1/', include(router_v1.urls)),
]
