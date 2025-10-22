from aiogram.types import User

from bsu.dtos import UserCreateDTO, UserDTO, NotificationUpdateDTO


def to_update_settings_dto(user: UserDTO):
    return NotificationUpdateDTO(
        user_id=user.user_id,
        min10=user.settings.min10,
        min5=user.settings.min5,
        min15=user.settings.min15,
        start_pair=user.settings.start_pair,
    )

def to_user_dto(tg_user: User):
    return UserCreateDTO(
        tg_user_id=tg_user.id,
        username=tg_user.username,
        first_name=tg_user.first_name,
        last_name=tg_user.last_name
    )

