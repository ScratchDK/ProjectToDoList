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
#from bot.dialogs.view_tasks import view_tasks_dialog
from bot.handlers.categories import categories_command
from bot.handlers.start import (new_task_command, start_command)
from bot.handlers.tasks import simple_tasks_command
from bot.handlers.test_handlers import test_api

logging.basicConfig(level=logging.INFO)


async def main():
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    # !!! Использовать REDIS + Persistence иначе при завершении данные будут утеряны !!!
    storage = MemoryStorage()   # Сохраняет состояние диалогов в оперативной памяти.
    dp = Dispatcher(storage=storage)   # Принимает сообщения от пользователя, выбирает и вызывает обработчики, маршрутизирует команды

    # Настройка маршрутизации. dp.message - "для входящих сообщений"
    dp.message.register(start_command, CommandStart()) # ↑ Создается новый dialog_manager с ПУСТЫМ dialog_data = {} 1️⃣

    # В данный момент не используется, показ задач идет не через диалог
    #dp.message.register(show_tasks_command, Command(commands=["tasks"]))
    dp.message.register(new_task_command, Command(commands=["new_task"]))
    dp.message.register(simple_tasks_command, Command(commands=["my_tasks"]))
    dp.message.register(categories_command, Command(commands=["categories"]))
    dp.message.register(test_api, Command("test_api"))

    # Регистрация диалогов
    dp.include_router(create_task_dialog)

    # В данный момент не используется, показ задач идет не через диалог
    #dp.include_router(view_tasks_dialog)   # "Добавь диалог просмотра задач в систему маршрутизации"

    setup_dialogs(dp)   # "Настрой всю систему диалогов в Dispatcher"

    try:
        await dp.start_polling(bot)
    # Правильное завершение, с сохранением данных
    finally:
        await dp.storage.close()   # Не имеет смысла, все равно данные будут потеряны
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
