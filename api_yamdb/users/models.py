from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _


class User(AbstractUser):
    is_moderator = models.BooleanField(
        _('moderator status'),
        default=False,
        help_text=_("Designates whether the user can use moderator's "
                    "permissions.")
    )
