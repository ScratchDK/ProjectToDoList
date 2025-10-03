from aiogram.filters.state import State, StatesGroup


class CreateTaskStates(StatesGroup):
    title = State()
    description = State()
    due_date = State()
    priority = State()
    categories = State()
    confirm = State()


class ViewTasksStates(StatesGroup):
    main = State()
    task_detail = State()
