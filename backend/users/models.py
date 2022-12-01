from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    CHAR_LIMIT: int = 150
    username = models.CharField(_('username'), max_length=CHAR_LIMIT,
                                unique=True,
                                validators=[UnicodeUsernameValidator()]
                                )
    email = models.EmailField(_('email'), unique=True, max_length=254)
    first_name = models.CharField(_('first_name'), max_length=CHAR_LIMIT)
    last_name = models.CharField(_('last_name'), max_length=CHAR_LIMIT)
    password = models.CharField(_('password'), max_length=CHAR_LIMIT)

    USERNAME_FIELD: str = 'email'
    REQUIRED_FIELDS = [
        'username', 'first_name', 'last_name'
    ]

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.username

    def recipes_count(self):
        return self.recipes.count()
