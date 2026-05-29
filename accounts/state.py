"""Reflex state for the user profile page."""

import reflex as rx
from reflex_django.auth.decorators import login_required
from reflex_django.states import AppState

from accounts.utils import (
    aget_or_create_profile,
    initials_from_name,
    save_user_avatar,
    validate_avatar_upload,
)


class ProfileState(AppState):
    display_name: str = ""
    email: str = ""
    notifications_enabled: bool = True
    avatar_url: str = ""
    avatar_initials: str = "?"
    upload_user_id: int | None = None

    @rx.event
    @login_required
    async def on_load_profile(self):
        await self.refresh_django_user_fields()
        user = self.request.user
        self.upload_user_id = user.pk
        profile = await aget_or_create_profile(user)
        self.display_name = profile.display_name or user.get_username()
        self.email = user.email or ""
        self.notifications_enabled = profile.notifications_enabled
        self.avatar_url = profile.avatar.url if profile.avatar else ""
        self.avatar_initials = initials_from_name(self.display_name)

    @rx.event
    @login_required
    async def handle_submit(self, form_data: dict):
        user = self.request.user
        self.upload_user_id = user.pk
        profile = await aget_or_create_profile(user)
        profile.display_name = form_data.get("name", profile.display_name)
        profile.notifications_enabled = self.notifications_enabled
        await profile.asave()

        user.email = form_data.get("email", user.email)
        await user.asave(update_fields=["email"])

        self.display_name = profile.display_name or user.get_username()
        self.email = user.email
        self.avatar_initials = initials_from_name(self.display_name)
        return rx.toast.success("Profile updated successfully", position="top-center")

    @rx.event
    @login_required
    async def toggle_notifications(self, checked: bool):
        self.notifications_enabled = checked
        user = self.request.user
        profile = await aget_or_create_profile(user)
        profile.notifications_enabled = checked
        await profile.asave()

    @rx.event
    async def handle_avatar_upload(self, files: list[rx.UploadFile]):
        if not files:
            return rx.toast.error("Choose an image first.", position="top-center")

        user = self.request.user
        if not getattr(user, "is_authenticated", False):
            return rx.toast.error(
                "Your session expired. Refresh the page and try again.",
                position="top-center",
            )

        upload = files[0]
        data = await upload.read()
        error = validate_avatar_upload(upload.filename or "avatar.jpg", data)
        if error:
            return rx.toast.error(error, position="top-center")

        profile = await aget_or_create_profile(user)
        self.avatar_url = await save_user_avatar(
            profile,
            upload.filename or "avatar.jpg",
            data,
        )
        return rx.toast.success("Profile photo updated.", position="top-center")
