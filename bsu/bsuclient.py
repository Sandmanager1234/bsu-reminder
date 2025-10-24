import os
import aiohttp
from typing import Optional, Dict
from datetime import datetime

from loguru import logger
from dotenv import load_dotenv

from bsu.exceptions import GroupDoesNotExist, ParameterError, ConnectionError

load_dotenv()


class BSUClient:
    base_url: str = os.getenv('BSU_API_URL')
    session: Optional[aiohttp.ClientSession] = None


    def start_session(self) -> aiohttp.ClientSession:
        """Создание aiohttp-сессии"""
        if self.session is None:
            self.session = aiohttp.ClientSession()

    async def close_session(self):
        """Явное закрытие aiohttp-сессии"""
        if self.session:
            await self.session.close()
            self.session = None

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        is_expected_html: bool = False
    ):
        """Приватный метод для выполнения HTTP-запросов к AmoCRM API с обработкой ошибок и логированием"""
        url = f"{self.base_url}{endpoint}"

        headers = {
            "Content-Type": "application/json",
        }

        logger.debug(
            f"Отправка {method}-запроса на {url} с параметрами: {params} и данными: {data}"
        )

        try:
            async with self.session.request(
                method, url, headers=headers, params=params, json=data
            ) as response:
                logger.info(
                    f"Ответ от сервера: статус {response.status} для {method}-запроса на {url}"
                )
                response.raise_for_status()  # Генерируем исключение, если статус-код не 200-299
                if is_expected_html:
                    return await response.text('utf8')
                return await response.json()  # Возвращаем JSON ответ
        except aiohttp.ClientResponseError as e:
            logger.error(f"Ошибка запроса: {e.status} {e.message}")
            if response.status == 400:
                response_data = await response.json()
                if response_data.get('error_description', '') == 'Не передан ID расписания':
                    raise GroupDoesNotExist
                raise ParameterError
            raise
        except aiohttp.ClientError as e:
            logger.error(f"Ошибка сети или соединения: {e}")
            raise ConnectionError


    async def get_schedule(self, group: int, period_start: datetime, period_end: datetime):
        params = {
            'from': period_start.strftime('%Y-%m-%d'),
            'to': period_end.strftime('%Y-%m-%d')
        }
        return await self._make_request('GET', f'/schedule/g/{group}', params=params)
