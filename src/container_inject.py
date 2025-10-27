from dependency_injector import containers, providers
from telegram.bot import TelegramBot
from bsu.bsuclient import BSUClient
from core.db import Database
from settings import Settings
from common.celery_app import CeleryApp
from redis import Redis

class Container(containers.DeclarativeContainer):
    
    config = providers.Singleton(Settings)
    wiring_config = containers.WiringConfiguration(
        packages=[
            "telegram.handlers", 
            "tasks.notify_tasks", 
            "tasks.query_tasks", 
            "tasks.schedule_tasks"
        ]
    )

    celery_app = providers.Singleton(
        CeleryApp,
        settings=config.provided.celery
    )
    database = providers.Singleton(
        Database,
        settings=config.provided.database
    )
    bsu_client = providers.Resource(
        BSUClient,
        settings=config.provided.bsu_client
    )
    telegram_bot = providers.Singleton(
        TelegramBot,
        settings=config.provided.telegram,
        db=database
    )
    
