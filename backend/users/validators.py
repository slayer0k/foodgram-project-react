from django.core.exceptions import ValidationError


def not_me(value):
    if value.lower() == 'me':
        raise ValidationError(
            'имя пользователя не может быть "me"'
        )
