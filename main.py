import os
import asyncio
import datetime
import aiofiles
import json


from bsu.bsuclient import BSUClient
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')

client = BSUClient()

def get_this_week():
    today = datetime.datetime.now()
    monday = today - datetime.timedelta(days=today.weekday())
    sunday = monday + datetime.timedelta(days=6)
    return monday.date().strftime('%Y-%m-%d'), sunday.date().strftime('%Y-%m-%d')


async def start():
    group = 12002532
    period_start, period_end = get_this_week()
    print(period_start, period_end)
    client.start_session()
    response = await client.get_schedule(group, period_start, period_end)
    client.close_session()
    async with aiofiles.open('schedule.json', 'w', encoding='utf8') as f:
        await f.write(json.dumps(response, ensure_ascii=False))



if __name__ == '__main__':
    asyncio.run(start())