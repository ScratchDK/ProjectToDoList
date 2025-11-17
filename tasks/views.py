from django.contrib.auth import get_user_model
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Category, Task
from .serializers import CategorySerializer, TaskSerializer

User = get_user_model()


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    # По умолчанию self.queryset.all()
    # В данный момент логика неправильная, потому что нарушает принцип REST из-за того что нужно дописывать параметр в путь
    # def get_queryset(self):
    #     """Возвращаем задачи по telegram_chat_id пользователя"""
    #     telegram_chat_id = self.request.query_params.get("telegram_chat_id")
    #
    #     if telegram_chat_id:
    #         try:
    #             user = User.objects.get(telegram_chat_id=telegram_chat_id)
    #             tasks = Task.objects.filter(user=user)
    #             return tasks
    #         except User.DoesNotExist:
    #             return Task.objects.none()
    #     return Task.objects.none()

    def get_queryset(self):
        user = self.request.user

        if not user.is_authenticated:
            return Task.objects.none()

        # Исполнитель видит только свои задачи
        if user.role == 'executor':
            return Task.objects.filter(user=user)

        # Менеджер видит задачи своих исполнителей
        elif user.role == 'manager':
            return Task.objects.filter(user__manager=user)

        # Админ видит все
        elif user.is_superuser:
            return Task.objects.all()

        return Task.objects.none()

    def perform_create(self, serializer):
        # Автоматически привязываем задачу к текущему пользователю
        serializer.save(user=self.request.user)

    # Старая логика, больше не нужна
    # def create(self, request, *args, **kwargs):
    #     telegram_chat_id = request.data.get("telegram_chat_id")
    #
    #     if not telegram_chat_id:
    #         return Response(
    #             {"error": "telegram_chat_id is required"},
    #             status=status.HTTP_400_BAD_REQUEST,
    #         )
    #
    #     # Находим пользователя
    #     try:
    #         user = User.objects.get(telegram_chat_id=telegram_chat_id)
    #     except User.DoesNotExist:
    #         return Response(
    #             {"error": "User not found. Please use /start command in bot first."},
    #             status=status.HTTP_404_NOT_FOUND,
    #         )
    #
    #     # Копируем данные и добавляем пользователя
    #     task_data = request.data.copy()
    #     task_data["user"] = user.id
    #     # НЕ добавляем telegram_chat_id в task_data - он уже в user!
    #
    #     # Обрабатываем категории
    #     categories_ids = task_data.pop("categories", [])
    #
    #     serializer = self.get_serializer(data=task_data)
    #     if serializer.is_valid():
    #         task = serializer.save()
    #
    #         # Добавляем категории если есть
    #         if categories_ids:
    #             categories = Category.objects.filter(id__in=categories_ids)
    #             task.categories.set(categories)
    #
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    queryset = Category.objects.all()
