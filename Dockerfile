FROM python:3.12-slim-bookworm

# Установка системных зависимостей + Poetry
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && rm -rf /var/lib/apt/lists/*

# Добавляем Poetry в PATH
ENV PATH="/root/.local/bin:$PATH"

# Рабочая директория
WORKDIR /app

# Копируем pyproject.toml и poetry.lock для кэширования
COPY pyproject.toml poetry.lock* ./

# Устанавливаем зависимости через Poetry
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Копируем остальные файлы проекта
COPY . .

# Команда для запуска сервера
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]