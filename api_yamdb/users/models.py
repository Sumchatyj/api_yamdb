import django.contrib.auth.models as django_auth_models
from django.contrib.auth.models import AbstractUser, AnonymousUser
from django.core import validators
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .validators import validate_username


class User(AbstractUser):
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"
    USER_CHOICES = [
        (ADMIN, _("admin")),
        (MODERATOR, _("moderator")),
        (USER, _("user")),
    ]
    username = models.CharField(
        _("username"),
        max_length=30,
        unique=True,
        help_text=_(
            "Required. 30 characters or fewer. Letters, digits and "
            "@/./+/-/_ only."
        ),
        validators=[
            validators.RegexValidator(
                r"^[\w.@+-]+$",
                _(
                    "Enter a valid username. "
                    "This value may contain only letters, numbers "
                    "and @/./+/-/_ characters."
                ),
                "invalid",
            ),
            validate_username,
        ],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    role = models.CharField(max_length=9, choices=USER_CHOICES, default=USER)
    bio = models.TextField(
        _("biography"),
        blank=True,
    )
    confirmation_code = models.CharField(
        max_length=128,
        blank=True,
    )

    def is_admin(self):
        if self.role == 'admin':
            return True

    def is_moderator(self):
        if self.role == 'moderator':
            return True


class AnonymousUserExtraFields(AnonymousUser):

    def is_admin(self):
        return False

    def is_moderator(self):
        return False


django_auth_models.AnonymousUser = AnonymousUserExtraFields
