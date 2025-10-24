from bot.bot import bot
from bsu.dtos import PairDTO
from bot.answers import subject_notify


async def send_reminder(user_id: int, pair: PairDTO, period: str):
    await bot.send_message(
        user_id, 
        subject_notify.format(
            start_period='cейчас' if period == 'start_peir' else f'через {period} минут',
            time_start=f'{pair.started_at.hour}:{pair.started_at.minute}',
            edtype=pair.edworkkind,
            subject=pair.dis,
            room= 'Онлайн' if pair.online else pair.room,
            teacher=pair.teacher_name
        )
    )