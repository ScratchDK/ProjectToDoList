import logging

from aiogram import Bot
from asgiref.sync import sync_to_async
from celery import shared_task
from django.conf import settings
from django.utils import timezone

from .models import Task

logger = logging.getLogger(__name__)


@shared_task
def send_telegram_task_notifications():
    """Отправка телеграм уведомлений о том что дата выполнения задачи наступила"""
    try:
        # Синхронная версия с использованием run_sync
        from asgiref.sync import async_to_sync

        result = async_to_sync(send_notifications_async)()
        return result

    except Exception as e:
        logger.error(f"Ошибка в задаче send_telegram_task_notifications: {e}")
        return f"Ошибка: {e}"


async def send_notifications_async():
    """Асинхронная часть отправки уведомлений"""
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)

    try:
        # Получаем задачи асинхронно
        due_tasks = await get_due_tasks()

        sent_count = 0
        for task in due_tasks:
            try:
                message = (
                    f"⏰ Напоминание о задаче!\n\n"
                    f"📝 {task.title}\n"
                    f"📅 Срок: {task.due_date.strftime('%d.%m.%Y')}\n"
                    f"🚨 Приоритет: {task.get_priority_display()}\n"
                    f"📊 Статус: {task.get_status_display()}"
                )

                await bot.send_message(chat_id=task.user.telegram_chat_id, text=message)
                await mark_task_as_notified(task)
                sent_count += 1

            except Exception as e:
                logger.error(f"Ошибка отправки уведомления для задачи {task.id}: {e}")

        logger.info(f"Отправлено телеграм уведомлений: {sent_count} задач")
        return f"Отправлено телеграм уведомлений: {sent_count} задач"

    finally:
        await bot.session.close()


@sync_to_async
def get_due_tasks():
    """Синхронная функция для получения задач"""
    now = timezone.now()
    return list(
        Task.objects.filter(
            due_date__lte=now,
            is_notified=False,
            status__in=["pending", "in_progress"],
            user__telegram_chat_id__isnull=False,
            user__telegram_notifications=True,
        ).select_related("user")
    )


@sync_to_async
def mark_task_as_notified(task):
    """Синхронная функция для пометки задачи как уведомленной"""
    task.is_notified = True
    task.save()
