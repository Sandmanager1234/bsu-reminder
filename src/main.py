import os
import asyncio

from container_inject import Container
from telegram.handlers import user_router
import logging

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)


container = Container()
celery = container.celery_app().get_app()

async def main():
    await container.init_resources()
    client = container.bsu_client()
    bot = container.telegram_bot()
    bot.register_handlers(user_router)
    await container.telegram_bot().start_bot()
    await container.shutdown_resources()
    

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())