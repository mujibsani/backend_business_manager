from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Application user for Business Manager.

    Roles:
        ADMIN   - Full system access
        MANAGER - Business/operational management
        STAFF   - Day-to-day operations
    """

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        MANAGER = "MANAGER", "Manager"
        STAFF = "STAFF", "Staff"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STAFF,
        db_index=True,
    )

    def __str__(self):
        return self.username

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN

    @property
    def is_manager_role(self):
        return self.role == self.Role.MANAGER

    @property
    def is_staff_role(self):
        return self.role == self.Role.STAFF