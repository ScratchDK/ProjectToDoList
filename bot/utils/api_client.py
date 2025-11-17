import os
from asgiref.sync import sync_to_async
from typing import Dict, List
from django.contrib.auth import get_user_model

import httpx
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model() # Получаем текущую модель user

class DjangoAPIClient:
    def __init__(self):
        self.base_url = os.getenv("DJANGO_API_URL", "http://localhost:8000") # Ищем в .env
        self.client = httpx.AsyncClient(
            limits=httpx.Limits(max_connections=10), timeout=30.0) # асинхронная версия HTTP клиента (как requests, но асинхронный)

    @sync_to_async
    def _get_user_and_token(self, telegram_chat_id: str):
        """Синхронный метод для получения пользователя и токена"""
        user = User.objects.get(telegram_chat_id=telegram_chat_id)
        token = AccessToken.for_user(user)
        return user, str(token)

    async def get_user_tasks(self, telegram_chat_id: str) -> List[Dict]:
        """Получить задачи пользователя по telegram_chat_id"""
        try:
            user, token = await self._get_user_and_token(telegram_chat_id)

            url = f"{self.base_url}/tasks/"
            #params = {"telegram_chat_id": telegram_chat_id}   убираем, потому что нарушает принцип REST
            headers = {'Authorization': f'Bearer {token}'} # Делаем запрос с токеном

            response = await self.client.get(url, headers=headers)

            print(f"Что внутри response - {response}")

            # Проверяет: Успешен ли HTTP запрос (статус 200-299) Если ошибка: Бросает исключение HTTPStatusError
            response.raise_for_status()
            data = response.json()

            print(f"Data - {data}")

            # Обрабатываем пагинацию DRF
            if isinstance(data, dict) and "results" in data:
                tasks = data["results"]
            else:
                tasks = data

            return tasks

        except httpx.HTTPStatusError as e:
            return []
        except Exception as e:
            return []

    async def create_task(self, task_data: Dict, telegram_chat_id: str) -> Dict:
        """Создать новую задачу для пользователя по telegram_chat_id"""
        try:
            #task_data["telegram_chat_id"] = telegram_chat_id   не нужно! Будем привязывать по JWT

            user, token = await self._get_user_and_token(telegram_chat_id)
            url = f"{self.base_url}/tasks/"

            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }

            print(f"🔍 DEBUG: URL: {url}")
            print(f"🔍 DEBUG: Headers: {headers}")
            print(f"🔍 DEBUG: Task data: {task_data}")
            print(f"🔍 DEBUG: Token: {token[:50]}...")  # Первые 50 символов токена

            response = await self.client.post(url, json=task_data, headers=headers)

            print(f"🔍 DEBUG: Response status: {response.status_code}")
            print(f"🔍 DEBUG: Response text: {response.text}")  # ← Важно!

            response.raise_for_status()
            return response.json()

        except Exception as e:
            raise e

    async def get_categories(self, telegram_chat_id: str) -> List[Dict]:
        """Получить список всех категорий"""
        try:
            user, token = await self._get_user_and_token(telegram_chat_id)

            url = f"{self.base_url}/categories/"
            headers = {'Authorization': f'Bearer {token}'}

            response = await self.client.get(url, headers=headers)

            response.raise_for_status()
            data = response.json()

            # Обрабатываем пагинацию DRF
            if isinstance(data, dict) and "results" in data:
                categories = data["results"]
            else:
                categories = data

            print(f"Доступные категорий - {categories}")
            return categories

        except httpx.HTTPStatusError as e:
            return []
        except Exception as e:
            return []


    async def get_executors(self, telegram_chat_id: str):
        print("Метод get_executors работает!")

        try:
            user, token = await self._get_user_and_token(telegram_chat_id)

            print(f"🔍 DEBUG: User role - {user.role}")
            print(f"🔍 DEBUG: Telegram chat ID - {telegram_chat_id}")
            print(f"🔍 DEBUG: User ID - {user.id}")

            url = f"{self.base_url}/users/executors/"
            headers = {'Authorization': f'Bearer {token}'}

            response = await self.client.get(url, headers=headers)

            print(f"🔍 DEBUG: Response status - {response.status_code}")
            print(f"🔍 DEBUG: Response text - {response.text}")

            response.raise_for_status()
            data = response.json()

            print(f"Data - {data}")

            return data

        except Exception as e:
            raise e




    # На будущее, в данный момент создание через админку
    # async def create_category(self, category_data: Dict) -> Dict:
    #     """Создать новую категорию"""
    #     try:
    #         response = await self.client.post(
    #             f"{self.base_url}/categories/", json=category_data, timeout=30.0
    #         )
    #
    #         response.raise_for_status()
    #         return response.json()
    #     except Exception as e:
    #         raise e
