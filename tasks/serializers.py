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
            "executors",
            "created_at",
            "updated_at",
            "is_overdue",
        ]
        read_only_fields = ["created_at", "updated_at", "user"]

    def create(self, validated_data):
        # Извлекаем ManyToMany поля ДО создания объекта
        categories_data = validated_data.pop("categories", [])
        executors_data = validated_data.pop("executors", [])

        print(f"Creating task with data: {validated_data}")  # для отладки

        # Создаем задачу БЕЗ ManyToMany полей
        task = Task.objects.create(**validated_data)

        # Добавляем категории если есть
        if categories_data:
            task.categories.set(categories_data)

        if executors_data:
            task.executors.set(executors_data)

        return task
