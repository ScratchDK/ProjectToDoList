from datetime import datetime

from aiogram import types, Router
from aiogram.filters import Command
from bot.utils.api_client import DjangoAPIClient

# Добавляем к существующему роутеру
router = Router()
api_client = DjangoAPIClient()


@router.message(Command("test_api"))
async def test_api(message: types.Message):
    """Тестирование API - команда /test_api"""
    try:
        await message.answer("🧪 Тестирую API...")

        chat_id = str(message.chat.id)\

        due_date = datetime.now()

        # 1. Тест получения задач
        tasks = await api_client.get_user_tasks(chat_id)
        task_count = len(tasks)
        await message.answer(f"1️⃣ Задачи: {task_count} шт. {'✅' if task_count >= 0 else '❌'}")

        # 2. Тест создания задачи
        task_data = {
            "title": f"Тестовая задача от {message.from_user.first_name}",
            "due_date": due_date.strftime("%Y-%m-%d")
        }
        created = await api_client.create_task(task_data, chat_id)
        creation_ok = "title" in created
        await message.answer(f"2️⃣ Создание задачи: {'✅' if creation_ok else '❌'}")

        # 3. Тест получения категорий
        categories = await api_client.get_categories(str(message.from_user.id))
        categories_ok = len(categories) >= 0
        await message.answer(f"3️⃣ Категории: {'✅' if categories_ok else '❌'}")

        # Итог
        if task_count >= 0 and creation_ok and categories_ok:
            await message.answer("🎉 Все тесты пройдены! API работает корректно.")
        else:
            await message.answer("⚠️ Есть проблемы с API. Проверь логи.")

    except Exception as e:
        await message.answer(f"❌ Критическая ошибка: {str(e)}")