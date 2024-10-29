"""Users serializers."""
from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    """User serializer."""

    pass
