from django.contrib import admin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        "telegram_chat_id",
        "email",
        "username",
        "role",
        "manager",
        "phone_number",
        "city",
        "is_staff",
        "last_login",
        "telegram_notifications",
    )
    list_display_links = ("email", "telegram_chat_id")
    list_filter = ("is_staff", "is_superuser", "is_active", "city", "role",)
    search_fields = ("email", "username", "phone_number", "telegram_chat_id")
    ordering = ("email",)

    fieldsets = (
        ("Основная информация", {
            "fields": (
                "email", "username", "first_name", "last_name",
                "role", "manager", "city"
            )
        }),
        ("Telegram данные", {
            "fields": (
                "telegram_chat_id", "telegram_username",
                "telegram_notifications"
            )
        }),
        ("Контакты", {
            "fields": ("phone_number",)
        }),
        ("Права доступа", {
            "fields": (
                "is_active", "is_staff", "is_superuser",
                "groups", "user_permissions"
            )
        }),
        ("Даты", {
            "fields": ("last_login", "date_joined")
        }),
    )