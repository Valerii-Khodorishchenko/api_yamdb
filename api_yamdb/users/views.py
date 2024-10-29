"""Users views."""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .serializers import UserSerializer
from .models import User
from .permissions import IsAdmin


class UserViewSet(viewsets.ModelViewSet):
    """Manage users."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    # lookup_field = 'username'