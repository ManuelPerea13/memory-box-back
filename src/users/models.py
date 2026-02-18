from django.contrib.auth.models import AbstractUser
from django.db import models


class AdminUser(AbstractUser):
    """Admin user for the Memory Box panel."""
    username = models.CharField(max_length=150, unique=True, blank=True)
    email = models.EmailField(unique=False, blank=True, null=True)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        if not self.pk and self.first_name and self.last_name:
            self.username = f"{self.first_name[0].lower()}{self.last_name.lower()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.pk} {self.username}"
