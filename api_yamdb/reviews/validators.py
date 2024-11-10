import datetime
import re

from django.conf import settings
from django.core.exceptions import ValidationError


def validate_username(username):
    if username == settings.RESERVED_NAME:
        raise ValidationError(
            f'Использование "{settings.RESERVED_NAME}" '
            'в качестве имени пользователя запрещено.'
        )
    if not re.match(r'^[\w.@+-]+\Z', username):
        raise ValidationError('Недопустимые символы в имени пользователя.')
    return username


def validate_year(year):
    if year > (current_year := datetime.date.today().year):
        raise ValidationError(
            f'Год выпуска ({year}) не может быть больше '
            f'текущего года ({current_year}).'
        )
    return year
