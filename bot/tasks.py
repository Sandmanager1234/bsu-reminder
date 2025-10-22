from bot.bot import bot


async def send_reminder(user_id: int, subject: str):
    await bot.send_message(user_id, f"Не забудь! Через 10 минут начнётся пара: {subject}")