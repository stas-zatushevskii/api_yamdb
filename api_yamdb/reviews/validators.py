from django.core.exceptions import ValidationError


def score_validation(value):
    if not (1 <= value <= 10):
        raise ValidationError('incorrect Score')


def text_validation(value):
    if not value:
        raise ValidationError('Необходимо записать текст')
