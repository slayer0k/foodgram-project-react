from django.core.exceptions import ValidationError


def bigger_than_zero(value):
    if value <= 0:
        raise ValidationError(
            'Значение должно быть больше нуля'
        )
