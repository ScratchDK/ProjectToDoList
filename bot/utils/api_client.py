import logging
import os
from typing import Dict, List, Optional

import httpx
from django.conf import settings

logger = logging.getLogger(__name__)


class DjangoAPIClient:
    def __init__(self):
        self.base_url = os.getenv("DJANGO_API_URL", "http://localhost:8000")
        logger.info(f"API Client using base URL: {self.base_url}")
        self.client = httpx.AsyncClient(timeout=30.0)

    async def get_user_tasks(self, telegram_chat_id: str) -> List[Dict]:
        """Получить задачи пользователя по telegram_chat_id"""
        try:
            logger.info(f"Requesting tasks for chat_id: {telegram_chat_id}")
            url = f"{self.base_url}/tasks/"
            params = {"telegram_chat_id": telegram_chat_id}

            logger.info(f"Making request to: {url} with params: {params}")

            response = await self.client.get(url, params=params)
            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response headers: {response.headers}")

            response.raise_for_status()
            data = response.json()

            logger.info(f"Raw response data: {data}")

            # Обрабатываем пагинацию DRF
            if isinstance(data, dict) and "results" in data:
                tasks = data["results"]
            else:
                tasks = data

            logger.info(f"Found {len(tasks)} tasks")
            return tasks

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP Error {e.response.status_code}: {e.response.text}")
            return []
        except Exception as e:
            logger.error(f"API Error get_user_tasks: {e}")
            return []

    async def create_task(self, task_data: Dict, telegram_chat_id: str) -> Dict:
        """Создать новую задачу для пользователя по telegram_chat_id"""
        try:
            task_data["telegram_chat_id"] = telegram_chat_id
            logger.info(f"Creating task: {task_data}")

            response = await self.client.post(
                f"{self.base_url}/tasks/", json=task_data, timeout=30.0
            )
            logger.info(f"Response status: {response.status_code}")

            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"API Error create_task: {e}")
            raise e

    async def get_categories(self) -> List[Dict]:
        """Получить список всех категорий"""
        try:
            logger.info("Requesting categories")
            response = await self.client.get(f"{self.base_url}/categories/")
            logger.info(f"Categories response status: {response.status_code}")

            response.raise_for_status()
            data = response.json()

            # Обрабатываем пагинацию DRF
            if isinstance(data, dict) and "results" in data:
                categories = data["results"]
            else:
                categories = data

            logger.info(f"Found {len(categories)} categories")
            return categories

        except Exception as e:
            logger.error(f"API Error get_categories: {e}")
            return []

    async def create_category(self, category_data: Dict) -> Dict:
        """Создать новую категорию"""
        try:
            logger.info(f"Creating category: {category_data}")
            response = await self.client.post(
                f"{self.base_url}/categories/", json=category_data, timeout=30.0
            )
            logger.info(f"Category creation response status: {response.status_code}")

            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"API Error create_category: {e}")
            raise e
