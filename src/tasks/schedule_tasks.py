import asyncio
from celery import shared_task
from datetime import timedelta
from dependency_injector.wiring import Provide, inject
from bsu.dtos import NotifyParams
from container_inject import Container
from core.db import Database
from bsu.bsuclient import BSUClient
from bsu.dependencies import get_service
from tasks.notify_tasks import send_notification_task
from tasks.dtos import UserNotifyCeleryTaskDTO
from tasks.service import TaskService



def weekly_collect_pairs_task():
    """Обёртка для запуска асинхронного обновления расписания"""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(weekly_collect_pairs())


@shared_task(name="weekly_collect_pairs_task")
@inject
async def weekly_collect_pairs(
    db: Database = Provide[Container.database],
    client: BSUClient = Provide[Container.bsu_client]
):
    async with db.create_session() as session:
        service = get_service(session, client)
        task_service = TaskService(session)
        groups = await service.get_all_groups()
        celery_tasks = []
        for group in groups:
            pairs = await service.collect_pairs(group.number, True)
            pairs_dto = await service.save_pairs(pairs, group.group_id)
            users = await service.get_all_users(group_id=group.group_id)

            for user in users:
                for notify_param in NotifyParams:
                    if getattr(user.settings, notify_param.value):
                        for pair_dto in pairs_dto:
                            eta = (
                                pair_dto.started_at
                                - timedelta(minutes=int(notify_param.value.removeprefix("min")))
                                if notify_param.value.startswith("min")
                                else pair_dto.started_at
                            )
                            result = send_notification_task.apply_async(
                                kwargs={
                                    "tg_user_id": user.tg_user_id,
                                    "pair_dto_data": pair_dto.model_dump(),
                                    "notify_param": notify_param.value,
                                },
                                eta=eta,
                            )
                            celery_tasks.append(
                                UserNotifyCeleryTaskDTO(
                                    task_id=result.id,
                                    user_id=user.user_id,
                                    group_id=user.group.group_id,
                                    notify_param=notify_param.value,
                                    started_at=eta
                                )
                            )
        if celery_tasks:
            await task_service.create_tasks(celery_tasks)