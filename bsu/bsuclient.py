import os
import aiohttp
from typing import Optional, Dict

from loguru import logger
from dotenv import load_dotenv

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
            raise
        except aiohttp.ClientError as e:
            logger.error(f"Ошибка сети или соединения: {e}")
            raise


    async def get_schedule(self, group: int, period_start: str, period_end: str):
        params = {
            'from': period_start,
            'to': period_end
        }
        return await self._make_request('GET', f'/schedule/g/{group}', params=params)
