from bsu.dtos import UserCreateDTO, NotificationUpdateDTO, UserDTO, PairGetDTO, PairDTO
from bsu.repository import BSURepository
from bsu.converters import to_update_settings_dto
from bsu.bsuclient import BSUClient
from modules.mytime import MyTime

class BSUService:
    def __init__(self, repo: BSURepository, client: BSUClient = None):
        self._repo = repo
        self._client = client

    async def get_or_create_user(self, user_dto: UserCreateDTO):
        user = await self._repo.get_users(user_dto)
        is_already_exist = True
        if not user:
            user = await self._repo.create_user(user_dto)
            is_already_exist = False
        return user, is_already_exist

    async def add_group_to_user(self, tg_user_id: int, group_number: int):
        group_dto = await self.get_or_create_group(group_number)
        await self._repo.change_group(tg_user_id, group_dto.group_id)
        return group_dto

    
    async def collect_pairs(self, group_number, is_next_week=False):
        start_week, end_week = MyTime.get_week_borders(is_next_week)
        pairs = await self._client.get_schedule(group_number, start_week, end_week)
        return pairs

    async def get_or_create_group(self, group_number: int):
        group = await self._repo.get_group(group_number)
        if not group:
            pairs = await self.collect_pairs(group_number)
            group = await self._repo.create_group(group_number)
            await self.save_pairs(pairs, group.group_id)
        return group 
    
    async def save_pairs(self, pairs_response, group_id):
        pairs_get_dto = [PairGetDTO.model_validate(pair_resp) for pair_resp in pairs_response]
        pairs_dto = [PairDTO.from_pair_get_dto(pair_get_dto, group_id) for pair_get_dto in pairs_get_dto]
        await self._repo.add_pairs(pairs_dto)
        return pairs_dto

    async def update_settings(self, user: UserDTO):
        update_settings_dto = to_update_settings_dto(user)
        # добавить / удалить таски
        await self._repo.update_settings(update_settings_dto)
    
    async def get_all_groups(self):
        return await self._repo.get_all_groups()
    
    async def get_all_users(self, group_id: int = None):
        return await self._repo.get_users(group_id = group_id)
    