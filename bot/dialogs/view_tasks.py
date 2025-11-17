from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Select
from aiogram_dialog.widgets.text import Const, Format, List

from bot.dialogs.states import ViewTasksStates
from bot.utils.api_client import DjangoAPIClient


async def get_tasks_data(dialog_manager: DialogManager, **kwargs):
    """Получить данные задач для отображения"""
    api_client = DjangoAPIClient()

    # Получаем задачи из API
    tasks_response = await api_client.get_user_tasks(
        str(dialog_manager.event.from_user.id)
    )

    print(f"Tasks response: {tasks_response}")

    # Обрабатываем пагинацию DRF (tasks могут быть в results)
    if isinstance(tasks_response, dict) and "results" in tasks_response:
        tasks = tasks_response["results"]
    else:
        tasks = tasks_response

    # Форматируем задачи для отображения
    formatted_tasks = []
    for task in tasks:
        # Форматируем дату создания
        created_at = task.get("created_at", "")
        if created_at:
            created_at = created_at.replace("T", " ").split(".")[0]

        formatted_tasks.append(
            {
                "id": task.get("id", ""),
                "title": task.get("title", "Без названия"),
                "created_at": created_at,
                "priority": task.get("priority", "medium"),
                "status": task.get("status", "pending"),
                "description": (
                    task.get("description", "")[:50] + "..."
                    if task.get("description")
                    else "Нет описания"
                ),
            }
        )

    return {"tasks": formatted_tasks, "count": len(formatted_tasks)}


async def on_task_selected(
    callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str
):
    """Обработчик выбора задачи"""
    await callback.answer(f"Задача {item_id}")


view_tasks_dialog = Dialog(
    Window(
        Format("📋 Ваши задачи ({count}):\n\n"),
        List(
            field=Format("{item.title} - {item.created_at}"),
            items="tasks",
            id="tasks_list",
        ),
        Button(Const("❌ Закрыть"), id="close", on_click=lambda c, w, d: d.done()),
        state=ViewTasksStates.main,
        getter=get_tasks_data,
    )
)
