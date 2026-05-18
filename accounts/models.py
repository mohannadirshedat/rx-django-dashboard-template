from django.conf import settings
from django.db import models


def avatar_upload_to(instance, filename: str) -> str:
    return f"avatars/user_{instance.user_id}/{filename}"


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    display_name = models.CharField(max_length=150, blank=True)
    notifications_enabled = models.BooleanField(default=True)
    avatar = models.ImageField(upload_to=avatar_upload_to, blank=True)

    def __str__(self) -> str:
        return self.display_name or str(self.user)
