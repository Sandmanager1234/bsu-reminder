import datetime

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import String, Integer, DateTime, Date, Boolean, JSON

from core.db import Base


class Group(Base):

    group_id = Column(Integer, primary_key=True, autoincrement=True)
    number = Column(Integer, unique=True, nullable=False)
    pairs = relationship('Pairs', back_populates='group')
    users = relationship('Users', back_populates='group')


class Pair(Base):
    
    __tablename__ = 'pair'

    pair_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    dis = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    started_at = Column(DateTime, nullable=False)
    group_id = Column(ForeignKey(Group.group_id, ondelete='CASCADE'))
    teacher_name = Column(String)

    edworkkind = Column(String)
    room = Column(String)
    online = Column(Boolean)

    links = Column(JSON)

    group = relationship(Group, back_populates='pairs')


class User(Base):
    __tablename__ = 'user'

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    tg_user_id = Column(Integer, unique=True, nullable=False)

    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    group_id = Column(ForeignKey(Group.group_id, ondelete='SET NULL'), nullable=True)

    is_admin = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone(offset=datetime.timedelta(hours=3))))

    group = relationship(Group, back_populates='users')
    settings = relationship('NotificationSettings', back_populates='user')


class NotificationSettings(Base):
    __tablename__ = 'notification_settings'

    notification_settings_id = Column(Integer, primary_key=True, autoincrement=True) 
    user_id = Column(ForeignKey(User.user_id, ondelete='CASCADE'), nullable=False, unique=True)
    min5 = Column(Boolean, default=False)
    min10 = Column(Boolean, default=False)
    min15 = Column(Boolean, default=False)
    start_pair = Column(Boolean, default=False)

    user = relationship(User, back_populates='settings')
