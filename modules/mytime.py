from datetime import datetime, timedelta, timezone, date




class MyTime:

    tz = timezone(offset=timedelta(hours=3))

    @classmethod
    def get_date(cls, ts: float | int):
        return cls.get_datetime(ts).date()
    
    @classmethod
    def get_datetime(cls, ts: int | float):
        return datetime.fromtimestamp(ts, cls.tz)
    
    @classmethod
    def get_current_ts(cls):
        return datetime.now(cls.tz).timestamp()
