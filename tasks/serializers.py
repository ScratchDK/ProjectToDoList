from rest_framework import serializers

from .models import Category, Task


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "created_at"]


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "due_date",
            "priority",
            "status",
            "categories",
            "user",
            "created_at",
            "updated_at",
            "is_overdue",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def create(self, validated_data):
        # Обрабатываем категории отдельно
        categories_data = validated_data.pop("categories", [])

        print(f"Creating task with data: {validated_data}")  # для отладки

        # Создаем задачу
        task = Task.objects.create(**validated_data)

        # Добавляем категории если есть
        if categories_data:
            task.categories.set(categories_data)

        return task
