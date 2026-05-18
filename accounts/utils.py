import uuid
from pathlib import Path

from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile

from .models import UserProfile

User = get_user_model()

ALLOWED_AVATAR_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


def initials_from_name(name: str) -> str:
    parts = [p for p in name.strip().split() if p]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()


def safe_avatar_filename(original: str) -> str:
    suffix = Path(original).suffix.lower()
    if suffix not in ALLOWED_AVATAR_EXTENSIONS:
        suffix = ".jpg"
    return f"{uuid.uuid4().hex}{suffix}"


async def aget_or_create_profile(user) -> UserProfile:
    """Return the user's profile, creating it if missing (e.g. pre-migration users)."""
    profile, _ = await UserProfile.objects.aget_or_create(user=user)
    return profile


@sync_to_async
def save_user_avatar(profile: UserProfile, filename: str, data: bytes) -> str:
    """Save avatar bytes to the profile; returns the public media URL."""
    if profile.avatar:
        profile.avatar.delete(save=False)

    safe_name = safe_avatar_filename(filename)
    profile.avatar.save(safe_name, ContentFile(data), save=True)
    return profile.avatar.url


def validate_avatar_upload(filename: str, data: bytes) -> str | None:
    """Return an error message, or None if valid."""
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_AVATAR_EXTENSIONS:
        return "Please upload a JPG, PNG, WebP, or GIF image."
    max_bytes = getattr(settings, "AVATAR_MAX_BYTES", 2 * 1024 * 1024)
    if len(data) > max_bytes:
        return "Image must be 2 MB or smaller."
    return None
