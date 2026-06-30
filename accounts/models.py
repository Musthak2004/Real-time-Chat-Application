from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class CustomUser(AbstractUser):

    email = models.EmailField(
        unique=True,
        verbose_name="email address",
    )

    phone_number = models.CharField(
        max_length=15,
        blank=True,
        verbose_name="phone number",
    )

    profile_picture = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True,
        verbose_name="profile picture",
    )

    bio = models.TextField(
        blank=True,
        verbose_name="bio",
    )

    date_of_birth = models.DateField(
        blank=True,
        null=True,
        verbose_name="date of birth",
    )

    is_online = models.BooleanField(
        default=False,
        verbose_name="online",
    )

    last_seen = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="last seen",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="created at",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="updated at",
    )

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = [
        "username"
    ]

    def clean(self):
        if self.date_of_birth and self.date_of_birth > timezone.now().date():
            raise ValidationError({"date_of_birth": "Date of birth cannot be in the future."})

    def __str__(self):
        return self.username