from django.contrib.auth import get_user_model
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Category, Task
from .serializers import CategorySerializer, TaskSerializer

User = get_user_model()


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """Возвращаем задачи по telegram_chat_id пользователя"""
        telegram_chat_id = self.request.query_params.get("telegram_chat_id")
        print(
            f"DEBUG: Looking for tasks with telegram_chat_id: {telegram_chat_id}"
        )  # для отладки

        if telegram_chat_id:
            try:
                user = User.objects.get(telegram_chat_id=telegram_chat_id)
                print(f"DEBUG: Found user: {user}")  # для отладки
                tasks = Task.objects.filter(user=user)
                print(f"DEBUG: Found {tasks.count()} tasks")  # для отладки
                return tasks
            except User.DoesNotExist:
                print(
                    f"DEBUG: User not found with telegram_chat_id: {telegram_chat_id}"
                )  # для отладки
                return Task.objects.none()
        print("DEBUG: No telegram_chat_id provided")  # для отладки
        return Task.objects.none()

    def create(self, request, *args, **kwargs):
        telegram_chat_id = request.data.get("telegram_chat_id")

        if not telegram_chat_id:
            return Response(
                {"error": "telegram_chat_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Находим пользователя
        try:
            user = User.objects.get(telegram_chat_id=telegram_chat_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found. Please use /start command in bot first."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Копируем данные и добавляем пользователя
        task_data = request.data.copy()
        task_data["user"] = user.id
        # НЕ добавляем telegram_chat_id в task_data - он уже в user!

        # Обрабатываем категории
        categories_ids = task_data.pop("categories", [])

        serializer = self.get_serializer(data=task_data)
        if serializer.is_valid():
            task = serializer.save()

            # Добавляем категории если есть
            if categories_ids:
                categories = Category.objects.filter(id__in=categories_ids)
                task.categories.set(categories)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    queryset = Category.objects.all()
