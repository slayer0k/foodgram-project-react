from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from users.validators import not_me


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username', 'first_name', 'last_name'
    ]

    username = models.CharField(
        _('username'), max_length=settings.CHAR_LIMIT,
        unique=True, validators=[UnicodeUsernameValidator(), not_me]
    )
    email = models.EmailField(
        _('email'), unique=True, max_length=settings.BIG_CHAR_LIMIT
    )
    first_name = models.CharField(
        _('first_name'), max_length=settings.CHAR_LIMIT
    )
    last_name = models.CharField(
        _('last_name'), max_length=settings.CHAR_LIMIT
    )
    password = models.CharField(
        _('password'), max_length=settings.CHAR_LIMIT
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.username

    def recipes_count(self):
        return self.recipes.count()
