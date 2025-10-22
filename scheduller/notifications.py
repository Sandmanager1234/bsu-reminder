from datetime import timedelta
from modules.mytime import MyTime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger

from scheduller.scheduller import scheduler
from bot.tasks import send_reminder


def schedule_lessons(lessons):
    for lesson in lessons:
        start_time = MyTime.get_datetime(lesson["start_time"])
        notify_time = start_time - timedelta(minutes=10)
        scheduler.add_job(
            send_reminder,
            trigger=DateTrigger(run_date=notify_time),
            args=[lesson["user_id"], lesson["subject"]],
            id=f"reminder_{lesson['user_id']}_{lesson['id']}",
            replace_existing=True
        )