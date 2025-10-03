# 📋 ToDo List - Django + Telegram Bot

Проект управления задачами с Telegram ботом и REST API.

## 🛠 Технологии
- **Backend**: Django + Django REST Framework
- **База данных**: PostgreSQL
- **Telegram Bot**: Aiogram + Aiogram Dialog
- **Фоновые задачи**: Celery + Redis
- **Деплой**: Docker + Docker Compose

## ⚙️ Требования
- Docker 20.10+
- Docker Compose 2.0+

## 🚀 Быстрый старт

1. Клонируйте репозиторий
   ```bash
   git clone https://github.com/ScratchDK/ProjectToDoList.git

2. Настройте окружение:
   ```bash
   cp .env.example .env
   cp .env.example .env.docker
   
3. Запустите проект:
    ```bash
    docker-compose up --build
   
## 📱 Telegram Bot
Бот автоматически запускается с проектом.

Доступные команды:
- /start - регистрация и приветствие
- /new_task - создать новую задачу
- /my_tasks - просмотр ваших задач
- /categories - список категорий

## 🌐 Web API
После запуска доступны:

- API: http://localhost:8000
- Админка: http://localhost:8000/admin
- Задачи: http://localhost:8000/tasks/
- Категории: http://localhost:8000/categories/

## 🛠 Управление сервисами

1. Остановить все сервисы:
    ```bash
    docker-compose down
   
2. Перезапустить конкретный сервис:
    ```bash
   docker-compose restart web
   docker-compose restart bot
   docker-compose restart celery_worker
   
3. Просмотр логов:
    ```bash
   docker-compose logs -f
   docker-compose logs bot -f
   docker-compose logs web -f
   
## 📦 Администрирование

1. Django миграции:
    ```bash
   docker-compose exec web python manage.py migrate
   
2. Создание суперпользователя:
    ```bash
   docker-compose exec web python manage.py createsuperuser
   
3. Пересборка проекта:
    ```bash
   docker-compose up -d --build
   
## 📩 Контакты
- Разработчик: Коваль Дмитрий Владимирович

- Email: desperado.ru@mail.ru