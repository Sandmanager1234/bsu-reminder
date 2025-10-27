
from sqlalchemy import Column
from sqlalchemy.types import String, Integer, DateTime, UUID
from core.db import Base



class UserNotifyCeleryTask(Base):
    __tablename__ = 'user_notify_task'

    task_id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(Integer)
    group_id = Column(Integer)
    notify_param = Column(String)
    started_at = Column(DateTime(timezone=True))