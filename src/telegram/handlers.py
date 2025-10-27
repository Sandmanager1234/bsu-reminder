import os
from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from dependency_injector.wiring import Provide, inject

from telegram.templates import (
    hello_msg, 
    insert_group_msg, 
    insert_group_msg_error,
    insert_group_msg_alredy_has,
    common_msg
)
from telegram.keyboards import menu, back_kb, periods_kb, get_times_kb
from telegram.fsm import States
from bsu.converters import to_user_dto
from telegram.exceptions import WrongFormatGroupNumber
from bsu.exceptions import GroupDoesNotExist, ConnectionError
from bsu.bsuclient import BSUClient
from container_inject import Container
from tasks.query_tasks import changed_group, changed_settings

from bsu.dependencies import get_service


user_router = Router()


@user_router.message(CommandStart())
async def start_message(msg: types.Message, session: AsyncSession):
    service = get_service(session)
    user_dto = to_user_dto(msg.from_user)
    user, is_already_exist = await service.get_or_create_user(user_dto)
    if is_already_exist:
        if user.group:
            await msg.answer(
                common_msg.format(group_number=user.group.number),
                reply_markup=menu
            )
    else:
        await msg.answer(
            hello_msg.format(name=msg.from_user.full_name),
            reply_markup=menu
        )


@user_router.callback_query(F.data == 'back')
async def back_to_menu(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await state.clear()
    service = get_service(session)
    user_dto = to_user_dto(callback.from_user)
    user, is_already_exist = await service.get_or_create_user(user_dto)
    if is_already_exist:
        if user.group:
            await callback.message.edit_text(
                common_msg.format(group_number=user.group.number),
                reply_markup=menu
            )
        else: 
            await callback.message.edit_text(
                hello_msg.format(name=callback.from_user.full_name),
                reply_markup=menu
            )
    else:
        await callback.message.edit_text(
            hello_msg.format(name=callback.from_user.full_name),
            reply_markup=menu
        )
    await callback.answer()


@user_router.callback_query(F.data == 'insert_group')
async def insert_group(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    service = get_service(session)
    user_dto = to_user_dto(callback.from_user)
    user, _ = await service.get_or_create_user(user_dto)
    await state.set_state(States.insert_group)
    await state.set_data({'msg': callback.message, 'old_group_id': user.group.group_id if user.group else None, 'user': user})
    
    if not user.group: # проверяем есть ли у пользователя группа
        await callback.message.edit_text(
            insert_group_msg,
            reply_markup=back_kb
        )
    else:
        await callback.message.edit_text(
            insert_group_msg_alredy_has.format(group=user.group.number),
            reply_markup=back_kb
        )
    await callback.answer()


@user_router.message(States.insert_group)
@inject
async def insertion_group(
    msg: types.Message, 
    state: FSMContext, 
    session: AsyncSession, 
    client: BSUClient = Provide[Container.bsu_client]
):
    service = get_service(session, client)
    data = await state.get_data()
    main_msg: types.Message = data['msg']
    old_group_id = data['old_group_id']
    user = data['user']
    try:
        group = msg.text.strip()
        if len(group) != 8:
            raise WrongFormatGroupNumber
        if not group.isdigit():
            raise WrongFormatGroupNumber
        group_number = int(group)
        group_dto = await service.add_group_to_user(
            msg.from_user.id,
            group_number
        )
        await state.clear()
        await main_msg.edit_text(
            common_msg.format(group_number=group_number),
            reply_markup=menu
        )
        msg.delete()
        changed_group.delay(
            user_dict=user.model_dump(),
            new_group_id=group_dto.group_id,
            old_group_id=old_group_id
        )
    except WrongFormatGroupNumber:
        await main_msg.edit_text(
            insert_group_msg_error.format(error='Неправильный формат номера группы'),
            reply_markup=back_kb
        )
    except GroupDoesNotExist:
        await main_msg.edit_text(
            insert_group_msg_error.format(error='Группа не существует или не найдена.'),
            reply_markup=back_kb
        )
    except ConnectionError:
        await main_msg.edit_text(
            insert_group_msg_error.format(error='Ошибка соединения с сервисом расписания. Попробуйте позже.'),
            reply_markup=back_kb
        )
    except Exception as ex:
        await main_msg.edit_text(
            insert_group_msg_error.format(error=ex),
            reply_markup=back_kb
        )


@user_router.callback_query(F.data == 'settings')
async def change_settings(callback: types.CallbackQuery, session: AsyncSession):
    service = get_service(session)
    user_dto = to_user_dto(callback.from_user)
    user, _ = await service.get_or_create_user(user_dto)

    await callback.message.edit_text(
        text='Выберите, когда уведомлять о начале пары!',
        reply_markup=get_times_kb(user.settings)
    )
    await callback.answer()


@user_router.callback_query(F.data.startswith("notify:"))
async def toggle_notification(callback: types.CallbackQuery, session: AsyncSession):
    _, key = callback.data.split(":")
    service = get_service(session)
    user_dto = to_user_dto(callback.from_user)
    user, _ = await service.get_or_create_user(user_dto)
    current = getattr(user.settings, key)
    setattr(user.settings, key, not current)
    await service.update_settings(user)
    await callback.message.edit_reply_markup(
        reply_markup=get_times_kb(user.settings)
    )
    changed_settings.delay(
        user_dict=user.model_dump(),
        group_id=user.group.group_id if user.group else None,
        notify_param=key
    )
    await callback.answer()
