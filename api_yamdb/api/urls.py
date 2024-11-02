<<<<<<< HEAD
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, GenreViewSet

router_v1 = DefaultRouter()
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('genres', GenreViewSet, basename='genres')

urlpatterns = [
    path('v1/', include(router_v1.urls)),
=======
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, SignupView, TokenObtainView


router_v1 = DefaultRouter()
router_v1.register('users', UserViewSet, basename='users')


urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/signup/', SignupView.as_view(), name='signup'),
    path('v1/auth/token/', TokenObtainView.as_view(), name='token_obtain'),
>>>>>>> 651b5ae721ac6a5dff7af52c3ac5a10dcb28a752
]
