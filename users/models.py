from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", 'Admin'
        ADMIN_PANEL = "ADMIN_PANEL", 'Admin Panel'
        CLIENT = "CLIENT", 'Client'

    last_activity = models.DateTimeField(null=True)
    base_role = Role.ADMIN
    role = models.CharField(max_length=50, choices=Role.choices)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.role = self.base_role

        return super().save(*args, **kwargs)
