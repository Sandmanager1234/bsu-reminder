import asyncio
from celery import shared_task
from dependency_injector.wiring import inject, Provide

from core.db import Database
from container_inject import Container
from tasks.service import TaskService
from bsu.dtos import UserDTO, NotifyParams
from tasks.dtos import UserNotifyCeleryTaskDTO

from datetime import timedelta
from tasks.notify_tasks import send_notification_task


@shared_task(name='user_changed_group')
@inject
def changed_group(
    user_dict: dict,
    new_group_id: int,
    old_group_id: int,
    db: Database = Provide[Container.database]

):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(changed_group_async(user_dict, new_group_id, old_group_id, db))

async def changed_group_async(
    user_dict: dict,
    new_group_id: int,
    old_group_id: int,
    db: Database
):
    user_dto = UserDTO.model_validate(user_dict)
    async with db.get_session() as session:
        service = TaskService(session)
        if old_group_id:
            tasks = await service.get_tasks_by_user(user_dto.user_id)
            app_control = send_notification_task.app.control
            for task in tasks:
                app_control.revoke(task.task_id, terminate=True) 
            await service.delete_tasks_by_user(user_dto.user_id, group_id=old_group_id)
        pairs = await service.get_pairs(new_group_id)
        celery_tasks = []
        for notify_param in NotifyParams:
            if getattr(user_dto.settings, notify_param.value):
                for pair in pairs:
                    eta = (
                        pair.started_at
                        - timedelta(minutes=int(notify_param.value.removeprefix("min")))
                        if notify_param.value.startswith("min")
                        else pair.started_at
                    )
                    result = send_notification_task.apply_async(
                        kwargs={
                            "tg_user_id": user_dto.tg_user_id,
                            "pair_dto_data": pair.model_dump(),
                            "notify_param": notify_param.value,
                        },
                        eta=eta,
                    )
                    celery_tasks.append(
                        UserNotifyCeleryTaskDTO(
                            task_id=result.id,
                            user_id=user_dto.user_id,
                            group_id=new_group_id,
                            notify_param=notify_param.value,
                            started_at=eta
                        )
                    )
        if celery_tasks:
            await service.create_tasks(celery_tasks)
                    

@shared_task(name='user_changed_settings')
@inject
def changed_settings(
    user_dict: dict,
    group_id: int, 
    notify_param: str,
    db: Database = Provide[Container.database]
):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(changed_settings_async(user_dict, group_id, notify_param, db))


async def changed_settings_async(
    user_dict: dict,
    group_id: int, 
    notify_param: str,
    db: Database
):
    user_dto = UserDTO.model_validate(user_dict)
    async with db.get_session() as session:
        async with session.begin():
            service = TaskService(session)

            if getattr(user_dto.settings, notify_param):
                if group_id:
                    pairs = await service.get_pairs(group_id)
                else:
                    pairs = []
                celery_tasks = []
                for pair in pairs:
                    eta = (
                        pair.started_at
                        - timedelta(minutes=int(notify_param.removeprefix("min")))
                        if notify_param.startswith("min")
                        else pair.started_at
                    )
                    result = send_notification_task.apply_async(
                        kwargs={
                            "tg_user_id": user_dto.tg_user_id,
                            "pair_dto_data": pair.model_dump(),
                            "notify_param": notify_param,
                        },
                        eta=eta
                    )
                    celery_tasks.append(UserNotifyCeleryTaskDTO(
                            task_id=result.id,
                            user_id=user_dto.user_id,
                            group_id=group_id,
                            notify_param=notify_param,
                            started_at=eta
                        )
                    )
                if celery_tasks:
                    await service.create_tasks(celery_tasks)
            else:
                tasks = await service.get_tasks_by_user(user_dto.user_id, notify_param)
                app_control = send_notification_task.app.control
                print(f'Количество тасков: {len(tasks)}')
                for task in tasks:
                    app_control.revoke(task.task_id, terminate=True) 
                await service.delete_tasks_by_user(user_dto.user_id, group_id=group_id, notify_param=notify_param)
    