from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet

router_v1 = DefaultRouter()
router_v1.register('categories', CategoryViewSet, basename='categories')

urlpatterns = [
    path('v1/', include(router_v1.urls)),
]
