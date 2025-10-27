from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class UserNotifyCeleryTaskDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    task_id: UUID
    user_id: int
    group_id: int
    notify_param: str
    started_at: datetime