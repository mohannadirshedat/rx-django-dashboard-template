"""Admin registration for the chatbot models."""

from django.contrib import admin

from chatbot.models import ChatMessage, ChatSession


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    fields = ("question", "answer", "created_at")
    readonly_fields = ("created_at",)


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "updated_at", "created_at")
    list_filter = ("owner",)
    search_fields = ("title", "owner__username")
    inlines = (ChatMessageInline,)


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("session", "question", "created_at")
    search_fields = ("question", "answer")
