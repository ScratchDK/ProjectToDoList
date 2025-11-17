from django.contrib.auth.models import (AbstractUser, BaseUserManager,
                                        PermissionsMixin)
from django.db import models
from django.core.exceptions import ValidationError


# Переопределяем objects для модели User, User.objects и т.д.
class CustomUserManager(BaseUserManager):
    def create_user(self, telegram_chat_id, password=None, **extra_fields):
        if not telegram_chat_id and not extra_fields["email"]:
            raise ValueError("Необходимо указать telegram_chat_id или email!")

        # Генерируем email если не предоставлен но есть telegram_chat_id
        if "email" not in extra_fields or not extra_fields["email"]:
            extra_fields["email"] = f"tg_{telegram_chat_id}@telegram.user"

        # normalize_email() - стандартный метод Django для нормализации email (приводит к нижнему регистру, обрезает пробелы)
        email = self.normalize_email(extra_fields["email"])

        # Убираем email из extra_fields чтобы не было дублирования
        extra_fields.pop("email", None)

        user = self.model(
            telegram_chat_id=telegram_chat_id, email=email, **extra_fields
        )

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()  # для Telegram users пароль не нужен

        user.save(using=self._db)
        return user

    def create_superuser(self, telegram_chat_id, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(telegram_chat_id, password, **extra_fields)


# Это встроенный миксин Django, который добавляет систему прав и разрешений
class CustomUser(AbstractUser, PermissionsMixin):
    CITY_CHOICES = [
        ("Pyatigorsk", "Пятигорск"),
        ("Moscow", "Москва"),
        ("Saint Petersburg", "Санкт-Петербург"),
        ("Omsk", "Омск"),
    ]

    ROLE_CHOICES = [
        ("manager", "Менеджер"),
        ("executor", "Исполнитель"),
    ]

    email = models.EmailField(unique=True, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    avatar = models.ImageField(upload_to="users/images/", blank=True, null=True)
    city = models.CharField(
        max_length=255,
        choices=CITY_CHOICES,
        null=True,
        blank=True,
        verbose_name="Город",
    )
    # Токен для потверждения почты при регестрации и для восстановления пароля
    confirmation_token = models.CharField(max_length=32, blank=True, null=True)
    telegram_notifications = models.BooleanField(
        default=True, verbose_name="Уведомления в Телеграм"
    )
    telegram_chat_id = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Телеграм chat-id",
        help_text="Укажите телеграм chat-id",
    )
    telegram_username = models.CharField(
        max_length=32, blank=True, null=True, verbose_name="Telegram username"
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    manager = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="executors",
        verbose_name="Менеджер",
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="executor")

    objects = CustomUserManager()

    USERNAME_FIELD = "telegram_chat_id"
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.telegram_chat_id} ({self.telegram_username or 'No username'})"

    def clean(self):
        super().clean()

        if self.manager == self:
            raise ValidationError("Пользователь не может быть менеджером для самого себя!")

        if self.manager and self.manager.role == 'manager' and self.role == 'manager':
            raise ValidationError('Менеджеру нельзя назначать другого менеджера!')

        if self.role == 'executor' and self.manager and self.manager.role == 'executor':
            raise ValidationError('Исполнитель не может быть менеджером другому исполнителю')

    def save(self, *args, **kwargs):
        self.clean()  # Вызываем валидацию перед сохранением
        super().save(*args, **kwargs)


    @classmethod
    def get_or_create_from_telegram(
        cls,
        chat_id: str,
        username: str = None,
        first_name: str = None,
        last_name: str = None,
    ):
        """Создает или получает пользователя по Telegram данным"""
        user, created = cls.objects.get_or_create(
            telegram_chat_id=chat_id,  # ← и для поиска, и для создания
            defaults={
                "telegram_username": username,
                "first_name": first_name or "",
                "last_name": last_name or "",
                "username": f"tg_{chat_id}",  # генерируем уникальное имя пользователя
                "email": f"tg_{chat_id}@telegram.user",  # генерируем уникальный email пользователя
                "role": "executor" # Новый пользователь по умолчанию исполнитель
            },
        )

        # Обновляем данные если пользователь уже существует
        if not created:
            updated = False
            if username and user.telegram_username != username:
                user.telegram_username = username
                updated = True
            if first_name and user.first_name != first_name:
                user.first_name = first_name
                updated = True
            if last_name and user.last_name != last_name:
                user.last_name = last_name
                updated = True

            if updated:
                user.save()

        return user, created
