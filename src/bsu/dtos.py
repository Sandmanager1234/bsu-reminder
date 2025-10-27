from enum import Enum
from typing import Optional
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict
from modules.mytime import MyTime


class NotifyParams(Enum):
    min15 = 'min15'
    min10 = 'min10'
    min5 = 'min5'
    start_pair = 'start_pair'


class UserGroupUpdateDTO(BaseModel):
    tg_user_id: int
    group: int


class UserGroupUpdateRepoDTO(BaseModel):
    tg_user_id: int
    group_id: int


class NotificationDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra='ignore')

    min5: bool = False
    min10: bool = False
    min15: bool = False
    start_pair: bool = False


class NotificationUpdateDTO(NotificationDTO):
    user_id: int


class UserCreateDTO(BaseModel):
    tg_user_id: int
    username: str
    first_name: Optional[str]
    last_name: Optional[str]
    is_admin: bool = False


class GroupDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    group_id: int
    number: int


class UserDTO(UserCreateDTO):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    tg_user_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    group: Optional[GroupDTO] = None
    settings: Optional[NotificationDTO] = None
    created_at: datetime


class TeacherGetDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    dep: str
    subdep: str
    pos: str



class PairGetDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    dis: str
    room: Optional[str]
    edworkkind: str
    timestart: int
    timeend: int
    subgroup: Optional[str]
    online: bool
    teacher: TeacherGetDTO
    links: list[dict]


class PairDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra='ignore')
    
    dis: str
    edworkkind: str
    date: date
    started_at: datetime
    group_id: int
    online: bool
    teacher_name: str
    room: Optional[str] = None
    links: list[dict]

    @classmethod
    def from_pair_get_dto(cls, pair: PairGetDTO, group_id: int) -> "PairDTO":
        self: PairDTO = cls(
            dis = pair.dis,
            edworkkind = pair.edworkkind,
            room = pair.room,
            online = pair.online,
            teacher_name = pair.teacher.name,
            links = pair.links,
            group_id = group_id,

            date = MyTime.get_date(pair.timestart),
            started_at = MyTime.get_datetime(pair.timestart)
        )
        return self
    