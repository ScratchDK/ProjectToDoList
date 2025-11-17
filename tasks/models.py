import secrets

from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils import timezone


def generate_custom_id():
    """Генератор уникального ID для моделей"""
    return secrets.token_urlsafe(12)


class CustomPKModel(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=16,
        unique=True,
        default=generate_custom_id,
        validators=[MinLengthValidator(12)],
    )

    class Meta:
        abstract = True


class Category(CustomPKModel):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Task(CustomPKModel):
    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateTimeField()
    priority = models.CharField(
        max_length=10, choices=PRIORITY_CHOICES, default="medium"
    )
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="pending")
    categories = models.ManyToManyField(Category, related_name="tasks", blank=True)
    user = models.ForeignKey(
        "users.CustomUser",
        on_delete=models.CASCADE,
        related_name="owner_task",
        verbose_name="Пользователь",
    )
    executors = models.ManyToManyField(
        "users.CustomUser",
        related_name="assigned_tasks",
        blank=True,
        verbose_name="Исполнители"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_notified = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        return self.due_date < timezone.now() and self.status != "completed"

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["due_date", "status"]),
            models.Index(fields=["user", "status"]),
        ]
