import datetime
import re

from django.core.exceptions import ValidationError

from api_yamdb.constants import RESERVED_NAME


def validate_username(username):
    if username == RESERVED_NAME:
        raise ValidationError(
            f'Использование "{RESERVED_NAME}" '
            'в качестве имени пользователя запрещено.'
        )
    regex = re.compile(r'^[\w.@+-]+$')
    if not regex.match(username):
        invalid_chars = ''.join(set(username) - set(regex.pattern))
        raise ValidationError(
            f'Имя пользователя содержит недопустимые символы: {invalid_chars}'
        )
    return username


def validate_year(year):
    current_year = datetime.date.today().year
    if year > current_year:
        raise ValidationError(
            f'Год выпуска ({year}) не может быть больше '
            f'текущего года ({current_year}).'
        )
    return year
