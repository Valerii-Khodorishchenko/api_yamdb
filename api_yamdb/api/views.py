from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAdminUser, AllowAny

from .serializers import CategorySerializer
from reviews.models import Category


class CategoryViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'

    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        elif self.action in ['create', 'destroy']:
            return [IsAdminUser()]
        return super().get_permissions()
