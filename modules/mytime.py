import calendar
from datetime import datetime, timedelta, timezone, date





class MyTime:

    tz = timezone(offset=timedelta(hours=3))

    @classmethod
    def get_current_datetime(cls):
        return datetime.now(cls.tz)

    @classmethod
    def get_date(cls, ts: float | int):
        return cls.get_datetime(ts).date()
    
    @classmethod
    def get_datetime(cls, ts: int | float):
        return datetime.fromtimestamp(ts, cls.tz)
    
    @classmethod
    def get_current_ts(cls):
        return datetime.now(cls.tz).timestamp()
    
    @classmethod
    def get_this_week(cls):
        now = cls.get_current_datetime()
        weekday = now.isoweekday() - 1
        start_week = now - timedelta(days=weekday)
        end_week = start_week + timedelta(days=6)
        return start_week, end_week
