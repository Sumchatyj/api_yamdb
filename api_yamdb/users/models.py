from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _


class User(AbstractUser):
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'
    USER_CHOICES = [
        (ADMIN, _('admin')),
        (MODERATOR, _('moderator')),
        (USER, _('user')),
    ]
    role = models.CharField(
        max_length=9,
        choices=USER_CHOICES,
        default=USER
    )
    bio = models.TextField(
        _('biography'),
        blank=True,
    )
    confirmation_code = models.CharField(
        max_length=128,
        blank=True,
    )
