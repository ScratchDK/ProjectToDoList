from datetime import datetime, timedelta

from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Back, Button, Cancel, Group, Row, Select
from aiogram_dialog.widgets.text import Const, Format

from bot.dialogs.states import CreateTaskStates
from bot.utils.api_client import DjangoAPIClient


async def on_title_input(_, __, dialog_manager, text):
    dialog_manager.dialog_data["title"] = text
    await dialog_manager.next()


async def on_description_input(_, __, dialog_manager, text):
    dialog_manager.dialog_data["description"] = text or ""
    await dialog_manager.next()


async def on_quick_date_selected(callback: CallbackQuery, widget, dialog_manager):
    """Обработчик быстрого выбора даты"""
    days_to_add = int(widget.widget_id)
    due_date = datetime.now() + timedelta(days=days_to_add)
    dialog_manager.dialog_data["due_date"] = due_date.strftime("%Y-%m-%d")
    await dialog_manager.next()


async def on_priority_selected(callback: CallbackQuery, widget, dialog_manager):
    dialog_manager.dialog_data["priority"] = widget.widget_id
    await dialog_manager.next()


async def on_category_selected(
    callback: CallbackQuery, widget, dialog_manager, item_id: str
):
    """Обработчик выбора категории"""
    selected_categories = dialog_manager.dialog_data.get("selected_categories", [])

    if item_id in selected_categories:
        selected_categories.remove(item_id)
    else:
        selected_categories.append(item_id)

    dialog_manager.dialog_data["selected_categories"] = selected_categories
    await callback.answer("Категория обновлена")


async def on_categories_confirm(callback: CallbackQuery, widget, dialog_manager):
    await dialog_manager.next()


async def create_task_final(callback: CallbackQuery, widget, dialog_manager):
    """Финальное создание задачи"""
    task_data = dialog_manager.dialog_data
    api_client = DjangoAPIClient()

    api_data = {
        "title": task_data["title"],
        "description": task_data.get("description", ""),
        "priority": task_data.get("priority", "medium"),
        "due_date": task_data.get("due_date", ""),
        "categories": task_data.get("selected_categories", []),
    }

    try:
        await api_client.create_task(api_data, str(callback.from_user.id))
        await callback.answer("✅ Задача создана!")
    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}")

    await dialog_manager.done()


async def categories_getter(dialog_manager: DialogManager, **kwargs):
    """Геттер для списка категорий"""
    api_client = DjangoAPIClient()
    categories = await api_client.get_categories()

    selected_categories = dialog_manager.dialog_data.get("selected_categories", [])

    category_items = []
    for category in categories:
        is_selected = category["id"] in selected_categories
        prefix = "✅" if is_selected else "◻️"
        category_items.append(
            {
                "id": category["id"],
                "name": f"{prefix} {category['name']}",
                "is_selected": is_selected,
            }
        )

    return {
        "categories": category_items,
        "selected_count": len(selected_categories),
        "categories_text": (
            ", ".join(
                [cat["name"] for cat in categories if cat["id"] in selected_categories]
            )
            if selected_categories
            else "не выбраны"
        ),
    }


async def priority_getter(dialog_manager: DialogManager, **kwargs):
    """Геттер для данных о приоритете"""
    priority = dialog_manager.dialog_data.get("priority", "medium")
    priority_display = {
        "high": "🔴 Высокий",
        "medium": "🟡 Средний",
        "low": "🟢 Низкий",
    }.get(priority, "🟡 Средний")

    # Форматируем дату для отображения
    due_date_str = dialog_manager.dialog_data.get("due_date", "")
    if due_date_str:
        due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
        due_display = due_date.strftime("%d.%m.%Y")
    else:
        due_display = "не установлена"

    api_client = DjangoAPIClient()
    all_categories = await api_client.get_categories()
    selected_categories = dialog_manager.dialog_data.get("selected_categories", [])
    selected_names = [
        cat["name"] for cat in all_categories if cat["id"] in selected_categories
    ]
    categories_text = ", ".join(selected_names) if selected_names else "не выбраны"

    return {
        "title": dialog_manager.dialog_data.get("title", ""),
        "description": dialog_manager.dialog_data.get("description", ""),
        "priority": priority_display,
        "due_date": due_display,
        "categories": categories_text,
    }


async def date_getter(dialog_manager: DialogManager, **kwargs):
    """Геттер для окна выбора даты"""
    return {
        "today": (datetime.now()).strftime("%d.%m.%Y"),
        "tomorrow": (datetime.now() + timedelta(days=1)).strftime("%d.%m.%Y"),
        "in_3_days": (datetime.now() + timedelta(days=3)).strftime("%d.%m.%Y"),
        "in_week": (datetime.now() + timedelta(days=7)).strftime("%d.%m.%Y"),
    }


create_task_dialog = Dialog(
    Window(
        Const("📝 Введите заголовок задачи:"),
        TextInput(
            id="title_input",
            on_success=on_title_input,
        ),
        Cancel(Const("❌ Отмена")),
        state=CreateTaskStates.title,
    ),
    Window(
        Const(
            "📄 Введите описание задачи (можно пропустить, отправьте любое сообщение):"
        ),
        TextInput(
            id="description_input",
            on_success=on_description_input,
        ),
        Back(Const("⬅️ Назад")),
        Cancel(Const("❌ Отмена")),
        state=CreateTaskStates.description,
    ),
    Window(
        Const("📅 Выберите дату выполнения:"),
        Row(
            Button(Const("📅 Сегодня"), id="0", on_click=on_quick_date_selected),
            Button(Const("📅 Завтра"), id="1", on_click=on_quick_date_selected),
        ),
        Row(
            Button(Const("📅 Через 3 дня"), id="3", on_click=on_quick_date_selected),
            Button(Const("📅 Через неделю"), id="7", on_click=on_quick_date_selected),
        ),
        Back(Const("⬅️ Назад")),
        Cancel(Const("❌ Отмена")),
        state=CreateTaskStates.due_date,
    ),
    Window(
        Const("🚨 Выберите приоритет:"),
        Row(
            Button(Const("🔴 Высокий"), id="high", on_click=on_priority_selected),
            Button(Const("🟡 Средний"), id="medium", on_click=on_priority_selected),
            Button(Const("🟢 Низкий"), id="low", on_click=on_priority_selected),
        ),
        Back(Const("⬅️ Назад")),
        Cancel(Const("❌ Отмена")),
        state=CreateTaskStates.priority,
    ),
    Window(
        Format("🏷️ Выберите категории ({selected_count} выбрано):\n\n"),
        Group(
            Select(
                Format("{item[name]}"),
                id="cat_sel",
                item_id_getter=lambda x: x["id"],
                items="categories",
                on_click=on_category_selected,
            ),
            width=1,
        ),
        Button(Const("✅ Продолжить"), id="continue", on_click=on_categories_confirm),
        Back(Const("⬅️ Назад")),
        Cancel(Const("❌ Отмена")),
        state=CreateTaskStates.categories,
        getter=categories_getter,
    ),
    Window(
        Format(
            "✅ Задача создана!\n\n"
            "📝 {title}\n"
            "📄 {description}\n"
            "🚨 Приоритет: {priority}\n"
            "📅 Срок: {due_date}\n"
            "🏷️ Категории: {categories}"
        ),
        Button(Const("Готово"), id="done", on_click=create_task_final),
        Back(Const("⬅️ Назад")),
        state=CreateTaskStates.confirm,
        getter=priority_getter,
    ),
)
