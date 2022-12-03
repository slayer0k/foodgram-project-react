from django.core.exceptions import ValidationError


def bigger_than_zero(value):
    if value < 1:
        raise ValidationError(
            'Значение не может быть меньше 1'
        )
