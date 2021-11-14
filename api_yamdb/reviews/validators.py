import datetime
from django.core.exceptions import ValidationError


def year_validation(year_value):
    if year_value > datetime.datetime.now().year:
        raise ValidationError(
            'Ошибка, %(value) больше текущего года!',
            params={'value': year_value},
        )


def score_validation(value):
    if not (1 <= value <= 10):
        raise ValidationError('incorrect Score')


def text_validation(value):
    if value == '':
        raise ValidationError('incorrect text')
