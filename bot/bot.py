import os
from aiogram import Bot, Dispatcher
from bot.handlers import user_router

from middlewares.db_sessions import DBSessionMiddleware


TOKEN = os.getenv('BOT_TOKEN')

bot = Bot(token=TOKEN)

dp = Dispatcher()
dp.message.middleware(DBSessionMiddleware())
dp.include_router(
    user_router
)