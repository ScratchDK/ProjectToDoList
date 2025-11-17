from aiogram import types
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model

User = get_user_model() # Получаем текущую модель user


@sync_to_async
def get_or_create_user(
    chat_id: str, username: str = None, first_name: str = None, last_name: str = None
):
    """Синхронная функция для создания/получения пользователя"""
    return User.get_or_create_from_telegram(
        chat_id=chat_id, username=username, first_name=first_name, last_name=last_name
    )


async def ensure_user_exists(message: types.Message):
    """Создает или получает пользователя по Telegram данным"""
    user, created = await get_or_create_user(
        chat_id=str(message.chat.id),
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )

    if created:
        print(f"✅ Создан новый пользователь: {user.telegram_chat_id}")
    else:
        print(f"✅ Найден существующий пользователь: {user.telegram_chat_id}")

    return user


async def start_with_registration(message: types.Message):
    """Команда /start с автоматической регистрацией"""
    user = await ensure_user_exists(message)

    welcome_text = (
        f"👋 Привет, {message.from_user.first_name or 'друг'}!\n\n"
        f"✅ Вы автоматически зарегистрированы!\n"
        f"🆔 Ваш ID: {user.telegram_chat_id}\n\n"
        f"📝 Доступные команды:\n"
        f"/tasks - 📋 Мои задачи\n"
        f"/new_task - ➕ Создать задачу\n"
        f"/categories - 🏷️ Категории\n\n"
        f"💡 Теперь вы можете создавать и просматривать свои задачи!"
    )

    await message.answer(welcome_text)
