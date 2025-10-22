from bsu.dtos import UserCreateDTO, NotificationUpdateDTO, UserDTO
from bsu.repository import BSURepository
from bsu.converters import to_update_settings_dto
from bsu.bsuclient import BSUClient

class BSUService:
    def __init__(self, repo: BSURepository, client: BSUClient):
        self._repo = repo
        self.client = client

    async def get_or_create_user(self, user_dto: UserCreateDTO):
        user = await self._repo.get_user(user_dto)
        is_already_exist = True
        if not user:
            user = await self._repo.create_user(user_dto)
            is_already_exist = False
        return user, is_already_exist

    async def add_group_to_user(self, tg_user_id: int, group_number: int):
        group_dto = await self.get_or_create_group(group_number)
        await self._repo.change_group(tg_user_id, group_dto.group_id)


    async def get_or_create_group(self, group_number: int):
        group = await self._repo.get_group(group_number)
        if not group:
            group = await self._repo.create_group(group_number)
            # спарсить группы
        return group 

    async def get_user_with_settings(self, user_dto: UserCreateDTO):
        return await self._repo.get_user_with_settings(user_dto)

    async def update_settings(self, user: UserDTO):
        update_settings_dto = to_update_settings_dto(user)
        await self._repo.update_settings(update_settings_dto)

    
    def add_pair(self):
        ...

    def get_group(self):
        ...

    