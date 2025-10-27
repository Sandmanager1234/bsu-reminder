from aiogram import BaseMiddleware
from typing import Callable, Awaitable, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from core.db import Database


class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, db: Database):
        self._db = db

    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any],
    ) -> Any:
        async with self._db.get_session() as session:
            data["session"] = session 
            try:
                # запускаем обработчик
                result = await handler(event, data)
                await session.commit()  # сохраняем изменения
                return result
            except Exception:
                await session.rollback()  # откатываем изменения при ошибке
                raise