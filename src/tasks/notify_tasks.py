import asyncio
from aiogram.utils.markdown import hlink
from aiogram.enums.parse_mode import ParseMode
from dependency_injector.wiring import Provide, inject
from bsu.dtos import PairDTO
from telegram.bot import TelegramBot
from container_inject import Container
from telegram.templates import subject_notify
from celery import shared_task


@shared_task(name="send_notification_task")
def send_notification_task(tg_user_id: int, pair_dto_data: dict, notify_param: str):
    asyncio.run(send_notification(tg_user_id, pair_dto_data, notify_param))



@inject
async def send_notification(
    tg_user_id: int,
    pair_dict: dict,
    notify_param: str,
    tgbot: TelegramBot = Provide[Container.telegram_bot]
):
    pair_dto = PairDTO.model_validate(pair_dict)
    await tgbot.bot.send_message(
        chat_id=tg_user_id,
        text=subject_notify.format(
            start_period=f'через {notify_param.removeprefix('min')} минут' if notify_param.startswith('min') else 'прямо сейчас',
            time_start=pair_dto.started_at.strftime('%H:%M'),
            edtype=pair_dto.edworkkind,
            subject=pair_dto.dis,
            room= 'Онлайн' if pair_dto.online else pair_dto.room,
            teacher=pair_dto.teacher_name,
            links = ' | '.join([hlink(link.get('name', ''), link.get('href', '')) for link in pair_dto.links]),
        ),
        parse_mode=ParseMode.HTML
    )
