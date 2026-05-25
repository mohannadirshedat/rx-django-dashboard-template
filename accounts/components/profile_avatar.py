"""Profile avatar display and upload widget."""

import reflex as rx

from accounts.state import ProfileState

_UPLOAD_ID = "avatar_upload"
_COLOR = "var(--accent-9)"


def profile_avatar_section() -> rx.Component:
    return rx.flex(
        rx.avatar(
            src=ProfileState.avatar_url,
            fallback=ProfileState.avatar_initials,
            size="8",
        ),
        rx.vstack(
            rx.upload(
                rx.vstack(
                    rx.button(
                        "Choose image",
                        variant="outline",
                        color_scheme="gray",
                    ),
                    rx.text(
                        "Drag and drop here, or click to browse",
                        size="2",
                        color="gray",
                    ),
                    spacing="2",
                    align="center",
                ),
                id=_UPLOAD_ID,
                max_files=1,
                accept={
                    "image/jpeg": [".jpg", ".jpeg"],
                    "image/png": [".png"],
                    "image/webp": [".webp"],
                    "image/gif": [".gif"],
                },
                border=f"1px dashed {_COLOR}",
                padding="1.5em",
                width="100%",
                on_drop=ProfileState.handle_avatar_upload(
                    rx.upload_files(upload_id=_UPLOAD_ID)
                ),
            ),
            rx.button(
                "Update photo",
                on_click=ProfileState.handle_avatar_upload(
                    rx.upload_files(upload_id=_UPLOAD_ID)
                ),
                width="100%",
            ),
            rx.text("JPG, PNG, WebP, or GIF. Max 2 MB.", size="1", color="gray"),
            spacing="3",
            width="100%",
            max_width="320px",
        ),
        spacing="6",
        align="center",
        width="100%",
        flex_direction=["column", "column", "row"],
    )
