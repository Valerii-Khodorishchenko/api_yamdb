import re

from django.core.exceptions import ValidationError
from django.conf import settings


def validate_username(username):
    if username == settings.RESERVED_NAME:
        raise ValidationError(
            f'Использование "{settings.RESERVED_NAME}" '
            'в качестве имени пользователя запрещено.'
        )
    regex = re.compile(r'^[\w.@+-]+$')
    if not re.match(regex, username):
        raise ValidationError(
            'Имя пользователя содержит недопустимые символы.'
        )
    return username
