from aiogram import types

from bot.utils.api_client import DjangoAPIClient


async def list_tasks(message: types.Message):
    """Показать список задач (простой вариант)"""
    api_client = DjangoAPIClient()

    # Получаем задачи
    tasks_response = await api_client.get_user_tasks(str(message.from_user.id))

    print(f"DEBUG tasks response: {tasks_response}")  # для отладки

    # Обрабатываем пагинацию DRF
    if isinstance(tasks_response, dict) and "results" in tasks_response:
        tasks = tasks_response["results"]
    else:
        tasks = tasks_response

    if not tasks:
        await message.answer("📭 У вас пока нет задач")
        return

    # Форматируем сообщение
    response = "📋 Ваши задачи:\n\n"
    for i, task in enumerate(tasks[:10], 1):  # Ограничим 10 задачами
        # Форматируем дату
        created_at = task.get("created_at", "")
        if created_at:
            created_at = created_at.replace("T", " ").split(".")[0]

        # Определяем эмодзи для приоритета
        priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(
            task.get("priority", "medium"), "🟡"
        )

        # Определяем эмодзи для статуса
        status_emoji = {
            "pending": "⏳",
            "in_progress": "🔄",
            "completed": "✅",
            "cancelled": "❌",
        }.get(task.get("status", "pending"), "⏳")

        response += (
            f"{i}. {task['title']}\n"
            f"   {priority_emoji} Приоритет: {task.get('priority', 'medium')}\n"
            f"   {status_emoji} Статус: {task.get('status', 'pending')}\n"
            f"   📅 Создана: {created_at}\n"
        )

        # Добавляем описание если есть
        description = task.get("description", "")
        if description:
            short_desc = (
                description[:50] + "..." if len(description) > 50 else description
            )
            response += f"   📄 Описание: {short_desc}\n"

        response += "   ───────────────\n"

    await message.answer(response)


# Простая команда для просмотра задач без диалога
async def simple_tasks_command(message: types.Message):
    await list_tasks(message)
