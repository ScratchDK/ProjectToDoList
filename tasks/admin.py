from django.contrib import admin

from .models import Category, Task


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["name"]
    readonly_fields = ["id", "created_at"]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "user",
        "status",
        "priority",
        "due_date",
        "is_overdue",
        "created_at",
    ]
    list_filter = ["status", "priority", "categories", "created_at", "due_date"]
    search_fields = ["title", "description", "user__username"]
    readonly_fields = ["id", "created_at", "updated_at", "is_notified"]
    filter_horizontal = ["categories"]
    date_hierarchy = "due_date"

    fieldsets = (
        ("Basic Information", {"fields": ("title", "description", "user")}),
        ("Details", {"fields": ("due_date", "priority", "status", "categories")}),
        (
            "System Information",
            {
                "fields": ("id", "created_at", "updated_at", "is_notified"),
                "classes": ("collapse",),
            },
        ),
    )
