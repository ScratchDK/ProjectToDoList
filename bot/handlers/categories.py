from aiogram import types

from bot.utils.api_client import DjangoAPIClient


async def list_categories(message: types.Message):
    """Показать список категорий"""
    api_client = DjangoAPIClient()

    # Получаем категории
    categories = await api_client.get_categories(str(message.from_user.id))

    if not categories:
        await message.answer(
            "🏷️ Категорий пока нет.\n\n"
            "Вы можете создать категории через веб-интерфейс:\n"
            "http://localhost:8000/categories/"
        )
        return

    # Форматируем сообщение
    response = "🏷️ Доступные категории:\n\n"
    for category in categories:
        response += f"📁 {category['name']}\n" f"🆔 ID: {category['id']}\n"

        # Добавляем дату создания если есть
        if category.get("created_at"):
            created_at = category["created_at"].replace("T", " ").split(".")[0]
            response += f"📅 Создана: {created_at}\n"

        response += f"───────────────\n"

    response += (
        "\n💡 Категории можно использовать при создании задач.\n"
        "Для создания новых категорий используйте веб-интерфейс."
    )

    await message.answer(response)


# Простая команда для просмотра категорий
async def categories_command(message: types.Message):
    await list_categories(message)
