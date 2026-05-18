from django.contrib import admin

from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "display_name", "notifications_enabled", "avatar")
    search_fields = ("user__username", "display_name")
