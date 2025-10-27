from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from settings import DatabaseSettings


class Base(DeclarativeBase):
    pass


class Database:
    def __init__(self, settings: DatabaseSettings):
        self._engine = create_async_engine(settings.db_url)
        self._session_maker = async_sessionmaker(self._engine, expire_on_commit=False)

    def get_session(self):
        return self._session_maker()
    
    def create_session(self):
        # Генератор для async context
        async def _session_gen():
            async with self._session_maker() as session:
                yield session
        return _session_gen()
    