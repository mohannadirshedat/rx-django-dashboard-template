"""Reflex state for the AI chatbot page.

Sessions and their question/answer messages are persisted in Django models
(:class:`chatbot.models.ChatSession` / :class:`chatbot.models.ChatMessage`).
Each answer is streamed token-by-token from the OpenAI API, flushing partial
state to the browser with ``yield`` after every delta.
"""

from typing import TypedDict

import reflex as rx
from reflex_django.auth.decorators import login_required
from reflex_django.states import AppState

from chatbot.models import ChatMessage, ChatSession
from core.secrets import secret_manager

DEFAULT_MODEL = "gpt-4o-mini"
SYSTEM_PROMPT = (
    "You are a helpful, friendly assistant embedded in the rxdjango dashboard. "
    "Answer concisely and use Markdown for formatting when it helps."
)


class QA(TypedDict):
    """A single question/answer exchange."""

    question: str
    answer: str


class ChatbotState(AppState):
    """Chat state backed by Django models."""

    sessions: list[dict] = []
    current_session_id: int = -1
    selected_chat: list[QA] = []
    processing: bool = False
    error: str = ""

    async def _load_sessions(self, user) -> None:
        self.sessions = [
            {"id": s.id, "title": s.title}
            async for s in ChatSession.objects.filter(owner=user)
        ]

    async def _load_messages(self) -> None:
        if self.current_session_id < 0:
            self.selected_chat = []
            return
        self.selected_chat = [
            {"question": m.question, "answer": m.answer}
            async for m in ChatMessage.objects.filter(
                session_id=self.current_session_id
            )
        ]

    @rx.event
    @login_required
    async def on_load(self):
        await self.refresh_django_user_fields()
        user = self.request.user
        if not getattr(user, "is_authenticated", False):
            self.sessions = []
            self.selected_chat = []
            self.current_session_id = -1
            return
        await self._load_sessions(user)
        if self.sessions:
            self.current_session_id = self.sessions[0]["id"]
            await self._load_messages()
        else:
            self.current_session_id = -1
            self.selected_chat = []

    @rx.event
    @login_required
    async def new_chat(self):
        await self.refresh_django_user_fields()
        user = self.request.user
        session = await ChatSession.objects.acreate(owner=user)
        self.current_session_id = session.id
        self.selected_chat = []
        self.error = ""
        await self._load_sessions(user)

    @rx.event
    @login_required
    async def select_chat(self, session_id: int):
        self.current_session_id = int(session_id)
        self.error = ""
        await self._load_messages()

    @rx.event
    @login_required
    async def delete_chat(self):
        if self.current_session_id < 0:
            return
        await self.refresh_django_user_fields()
        user = self.request.user
        await ChatSession.objects.filter(
            id=self.current_session_id, owner=user
        ).adelete()
        await self._load_sessions(user)
        if self.sessions:
            self.current_session_id = self.sessions[0]["id"]
            await self._load_messages()
        else:
            self.current_session_id = -1
            self.selected_chat = []

    @rx.event
    @login_required
    async def process_question(self, form_data: dict):
        question = (form_data.get("question") or "").strip()
        if not question or self.processing:
            return

        api_key = secret_manager.get_secret("OPENAI_API_KEY", default="")
        if not api_key:
            self.error = "OPENAI_API_KEY is not set."
            yield rx.toast.error(
                "OpenAI is not configured. Set OPENAI_API_KEY and restart.",
                position="top-center",
            )
            return

        await self.refresh_django_user_fields()
        user = self.request.user
        self.error = ""

        first_message = not self.selected_chat
        if self.current_session_id < 0:
            session = await ChatSession.objects.acreate(
                owner=user, title=question[:60]
            )
            self.current_session_id = session.id
        else:
            session = await ChatSession.objects.aget(
                id=self.current_session_id, owner=user
            )
            if first_message:
                session.title = question[:60]
                await session.asave(update_fields=["title"])

        message = await ChatMessage.objects.acreate(
            session=session, question=question, answer=""
        )
        self.selected_chat.append({"question": question, "answer": ""})
        self.selected_chat = self.selected_chat
        self.processing = True
        yield

        api_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for qa in self.selected_chat[:-1]:
            api_messages.append({"role": "user", "content": qa["question"]})
            api_messages.append({"role": "assistant", "content": qa["answer"]})
        api_messages.append({"role": "user", "content": question})

        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=api_key)
            model = secret_manager.get_secret("OPENAI_CHAT_MODEL", default=DEFAULT_MODEL)

            async with client.chat.completions.stream(
                model=model,
                messages=api_messages,
            ) as stream:
                async for event in stream:
                    if event.type == "content.delta":
                        self.selected_chat[-1]["answer"] += event.delta
                        self.selected_chat = self.selected_chat
                        yield

            message.answer = self.selected_chat[-1]["answer"]
            await message.asave(update_fields=["answer"])
            await session.asave()
            await self._load_sessions(user)
        except Exception as exc:  # noqa: BLE001 - surface any API/network error in the UI
            self.error = str(exc)
            self.selected_chat[-1]["answer"] += f"\n\n_Error: {exc}_"
            self.selected_chat = self.selected_chat
            message.answer = self.selected_chat[-1]["answer"]
            await message.asave(update_fields=["answer"])
            yield rx.toast.error(f"Chat failed: {exc}", position="top-center")
        finally:
            self.processing = False
            yield
