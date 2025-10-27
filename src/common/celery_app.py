import os
from celery import Celery
from celery.schedules import crontab

from settings import CelerySettings


class CeleryApp:
    def __init__(self, settings: CelerySettings):
        self.app = Celery(
            "bot_tasks",
            broker=settings.broker_url,
            backend=settings.backend_url
        )
        self.app.conf.update(
            task_serializer='json',
            result_serializer='json',
            accept_content=['json'],
            timezone='Europe/Moscow',
            enable_utc=True,
            task_routes={}
        )
    
        self.app.conf.beat_schedule = {
            "collect-pairs-weekly": {
                "task": "weekly_collect_pairs_task",
                "schedule": crontab(hour=0, minute=0, day_of_week="sun"), 
            },
        }

    def get_app(self):
        return self.app
    