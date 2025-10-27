from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from bsu.dtos import PairDTO, UserCreateDTO, UserDTO, GroupDTO, NotificationUpdateDTO
from bsu.models import Pair, User, NotificationSettings, Group


class BSURepository:
    def __init__(self, session: AsyncSession):
        self._session = session
 
    async def get_users(
        self,
        user_dto: UserCreateDTO = None,
        group_id: int = None
    ):
        q = (
            select(User)
            .options(
                selectinload(User.group),
                selectinload(User.settings)
            )
        )
        if user_dto:
            q = q.where(User.tg_user_id == user_dto.tg_user_id)
        if group_id:
            q = q.where(User.group_id == group_id)
        result = await self._session.execute(q)
        users = result.scalars().all()
        if users:
            users_dto = [UserDTO.model_validate(user) for user in users]
            if len(users_dto) == 1:
                return users_dto[0]
            return users_dto
        return None

    async def create_user(self, user_dto: UserCreateDTO):
            user = User(**user_dto.model_dump())
            self._session.add(user)
            await self._session.flush()
            await self._create_notification_for_user(user.user_id)
            await self._session.refresh(user, ["settings"])
            return UserDTO.model_validate(user)
    
    async def _create_notification_for_user(self, user_id):
        settings = NotificationSettings(user_id=user_id)
        self._session.add(settings)
        await self._session.flush()

    async def change_group(self, tg_user_id: int, group_id: int):
        await self._session.execute(
            update(User)
            .where(User.tg_user_id == tg_user_id)
            .values(group_id=group_id)
        )
    
    async def add_pairs(self, pairs_dtos: list[PairDTO]):
        pairs = [Pair(**pair_dto.model_dump()) for pair_dto in pairs_dtos]
        self._session.add_all(pairs)
        await self._session.flush()

    async def get_schedule(self, period_start, period_end):
        result = await self._session.execute(
            select(Pair)
            .select_from(Pair)
            .where(
                Pair.started_at >= period_start,
                Pair.started_at <= period_end
            )
        )
        pairs = result.scalars().all()
        return [PairDTO.model_dump(pair) for pair in pairs]
    
    async def get_group(self, group_number: int):
        result = await self._session.execute(
            select(Group)
            .where(Group.number == group_number)
        )        
        group = result.scalar_one_or_none()
        if group:
            return GroupDTO.model_validate(group)
        return None

    async def create_group(self, group_number: int):
        group = Group(number=group_number)
        self._session.add(group)
        await self._session.flush()
        return GroupDTO.model_validate(group)
    
    async def update_settings(self, settings_dto: NotificationUpdateDTO):
        user_id = settings_dto.user_id
        result = await self._session.execute(
            select(NotificationSettings)
            .where(NotificationSettings.user_id == user_id)
        )
        settings = result.scalar_one_or_none()
        if not settings:
            raise ValueError(f"Settings for user {user_id} not found")
        for key, value in settings_dto.model_dump(exclude_unset=True).items():
            if hasattr(settings, key):
                setattr(settings, key, value)
        await self._session.flush()

    async def get_all_groups(self):
        result = await self._session.execute(select(Group))
        return [GroupDTO.model_validate(group) for group in result.scalars()]
    


    async def delete_old_pairs(self, delete_time):
        ...