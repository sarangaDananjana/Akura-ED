from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


class CustomUser(AbstractUser):
    """
    Custom user model to handle premium access and learning preferences.
    """
    is_premium = models.BooleanField(
        default=False, help_text="Designates whether this user has paid for premium content.")
    daily_flashcard_limit = models.IntegerField(
        default=10, help_text="User's selected daily workload (e.g., 10, 20, 50).")

    # Add any other profile fields you might need
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    auth_version = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return f"{self.username}"
