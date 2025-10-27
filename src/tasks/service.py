
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from tasks.models import UserNotifyCeleryTask
from tasks.dtos import UserNotifyCeleryTaskDTO
from bsu.models import Pair
from bsu.dtos import PairDTO
from datetime import datetime
from modules.mytime import MyTime


class TaskService:
    
    def __init__(self, session: AsyncSession):
        self._session = session

    
    async def get_tasks_by_user(self, user_id: int, notify_param: str = None) -> list[UserNotifyCeleryTaskDTO]:
        filters = []
        filters.append(UserNotifyCeleryTask.user_id == user_id)
        if notify_param:
            filters.append(UserNotifyCeleryTask.notify_param == notify_param)
        q = (
            select(
                UserNotifyCeleryTask
            ).where(*filters)
        )
        result = await self._session.execute(q)
        return [UserNotifyCeleryTaskDTO.model_validate(task) for task in result.scalars().all()]

    async def delete_tasks_by_user(self, user_id: int, notify_param: str = None, group_id: int = None):
        filters = []
        filters.append(UserNotifyCeleryTask.user_id == user_id)
        if notify_param:
            filters.append(UserNotifyCeleryTask.notify_param == notify_param)
        if group_id:
            filters.append(UserNotifyCeleryTask.group_id == group_id)
        q = (
            delete(
                UserNotifyCeleryTask
            ).where(*filters)
        )
        await self._session.execute(q)
        await self._session.flush()
        await self._session.commit()

    async def create_tasks(self, task_dtos: list[UserNotifyCeleryTaskDTO]):
        tasks = [UserNotifyCeleryTask(**task_dto.model_dump()) for task_dto in task_dtos]
        self._session.add_all(tasks)
        await self._session.flush()
        await self._session.commit()
    
    async def get_pairs(self, group_id: int):
        q = (
            select(Pair)
            .where(Pair.group_id == group_id)
            .where(Pair.started_at >= MyTime.get_current_datetime())
        )
        result = await self._session.execute(q)
        return [PairDTO.model_validate(pair) for pair in result.scalars().all()]