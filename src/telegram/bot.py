import os
from aiogram import Bot, Dispatcher, Router

from middlewares.db_sessions import DbSessionMiddleware
from core.db import Database

from settings import TelegramSettings


class TelegramBot:
    def __init__(self, settings: TelegramSettings, db: Database):
        self.bot = Bot(token=settings.token)
        self.dp = Dispatcher()
        self.dp.update.middleware(DbSessionMiddleware(db))

    
    def register_handlers(self, *routers: Router):
        self.dp.include_routers(
            *routers
        )
    
    async def start_bot(self):
        await self.dp.start_polling(self.bot)