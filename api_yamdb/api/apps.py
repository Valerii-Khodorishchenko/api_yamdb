"""API apps."""
from django.apps import AppConfig


class ApiConfig(AppConfig):
    """API config."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
