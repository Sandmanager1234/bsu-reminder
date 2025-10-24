from datetime import timedelta
from modules.mytime import MyTime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger

from scheduler.scheduler import scheduler


def schedule_lessons(lessons, func: function):
    for lesson in lessons:
        start_time = MyTime.get_datetime(lesson["start_time"])
        notify_time = start_time - timedelta(minutes=10)
        scheduler.add_job(
            func,
            trigger=DateTrigger(run_date=notify_time),
            args=[lesson["user_id"], lesson["subject"]],
            id=f"reminder_{lesson['user_id']}_{lesson['id']}",
            replace_existing=True
        )