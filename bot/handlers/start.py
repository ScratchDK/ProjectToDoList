from aiogram import types
from aiogram_dialog import DialogManager, StartMode

from bot.dialogs.states import CreateTaskStates, ViewTasksStates
from bot.handlers.auth import ensure_user_exists


async def start_command(message: types.Message):
    # Автоматически создаем/получаем пользователя
    user = await ensure_user_exists(message)

    await message.answer(
        f"👋 Привет, {message.from_user.first_name or 'друг'}!\n\n"
        "📝 Доступные команды:\n"
        "/my_tasks - 📋 Мои задачи\n"
        "/new_task - ➕ Создать задачу\n"
        "/categories - 🏷️ Категории"
    )


async def show_tasks_command(message: types.Message, dialog_manager: DialogManager):
    # Убеждаемся что пользователь существует
    await ensure_user_exists(message)
    await dialog_manager.start(ViewTasksStates.main, mode=StartMode.RESET_STACK)


async def new_task_command(message: types.Message, dialog_manager: DialogManager):
    # Убеждаемся что пользователь существует
    await ensure_user_exists(message)
    await dialog_manager.start(CreateTaskStates.title, mode=StartMode.RESET_STACK)
