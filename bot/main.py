import asyncio
import logging
import os
import sys

import django
from django.conf import settings

# Добавляем путь к корню проекта
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Настраиваем Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram_dialog import setup_dialogs

from bot.dialogs.create_task import create_task_dialog
from bot.dialogs.view_tasks import view_tasks_dialog
from bot.handlers.categories import categories_command
from bot.handlers.start import (new_task_command, show_tasks_command,
                                start_command)
from bot.handlers.tasks import list_tasks, simple_tasks_command

logging.basicConfig(level=logging.INFO)


async def main():
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # ПРАВИЛЬНАЯ регистрация команд для aiogram 3.x
    dp.message.register(start_command, CommandStart())
    dp.message.register(show_tasks_command, Command(commands=["tasks"]))
    dp.message.register(new_task_command, Command(commands=["new_task"]))
    dp.message.register(simple_tasks_command, Command(commands=["my_tasks"]))
    dp.message.register(categories_command, Command(commands=["categories"]))

    # Регистрация диалогов
    dp.include_router(create_task_dialog)
    dp.include_router(view_tasks_dialog)

    setup_dialogs(dp)

    try:
        await dp.start_polling(bot)
    finally:
        await dp.storage.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
