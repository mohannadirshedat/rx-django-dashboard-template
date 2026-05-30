"""Reflex pages for the chatbot app (auto-discovered by reflex-django)."""

import reflex as rx

from chatbot.components.chat import action_bar, chat, sessions_bar
from chatbot.state import ChatbotState
from dashboard.templates import template


@template(
    route="/chatbot",
    title="Chatbot",
    login_required=True,
    on_load=ChatbotState.on_load,
)
def chatbot() -> rx.Component:
    """Render the AI chatbot page."""
    return rx.vstack(
        sessions_bar(),
        rx.cond(
            ChatbotState.error != "",
            rx.callout(
                ChatbotState.error,
                icon="triangle_alert",
                color_scheme="red",
                width="100%",
                max_width="50em",
                margin_inline="auto",
            ),
        ),
        chat(),
        action_bar(),
        spacing="4",
        width="100%",
        height="calc(100vh - 9rem)",
    )
