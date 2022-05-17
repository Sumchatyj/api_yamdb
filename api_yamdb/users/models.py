from django.contrib.auth.models import AbstractUser, AnonymousUser
from django.core import validators
from django.db import models
from django.utils.translation import ugettext_lazy as _
from .validators import validate_username
import django.contrib.auth.models as django_auth_models


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
    is_moderator = models.BooleanField(
        _("moderator status"),
        default=False,
        help_text=_("Designates whether the user have moderator status"),
    )
    is_admin = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user have moderator admin"),
    )

    def save(self, *args, **kwargs):
        if self.role == "moderator":
            self.is_moderator = True
        if self.role == "admin":
            self.is_admin = True
        super(User, self).save(*args, **kwargs)


class AnonymousUserExtraFields(AnonymousUser):
    is_moderator = False
    is_admin = False


django_auth_models.AnonymousUser = AnonymousUserExtraFields
