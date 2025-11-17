from aiogram.filters.state import State, StatesGroup


# С FSM бот помнит, где находится пользователь
# Скелет будущего диалога с пользователем
class CreateTaskStates(StatesGroup):
    title = State()           # Шаг 1: Ввод заголовка
    description = State()     # Шаг 2: Ввод описания
    due_date = State()        # Шаг 3: Выбор даты
    priority = State()        # Шаг 4: Выбор приоритета
    executors = State()       # Шаг 5: Выбор исполнителей
    categories = State()      # Шаг 6: Выбор категорий
    confirm = State()         # Шаг 7: Подтверждение


# В данный момент не используется, показ задач идет не через диалог
# class ViewTasksStates(StatesGroup):
#     main = State()
#     task_detail = State()
