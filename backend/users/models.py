from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    username = models.CharField(_('username'), max_length=150, unique=True,
                                validators=[
                                    UnicodeUsernameValidator(), ])
    email = models.EmailField(_('email'), unique=True, max_length=254)
    first_name = models.CharField(_('first_name'), max_length=150)
    last_name = models.CharField(_('last_name'), max_length=150)
    password = models.CharField(_('password'), max_length=150)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.username

    def recipes_count(self):
        return self.recipes.count()
