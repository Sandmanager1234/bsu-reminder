from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession


class Base(DeclarativeBase):
    pass


engine = create_async_engine(...)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
