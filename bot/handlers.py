import os
from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot.answers import (
    hello_msg, 
    insert_group_msg, 
    insert_group_msg_error,
    insert_group_msg_alredy_has
)
from bot.keyboards import menu, back_kb, periods_kb, get_times_kb
from bot.fsm import States
from bsu.converters import to_user_dto
from bot.exceptions import WrongFormatGroupNumber, GroupDoesNotExistOrTooOld

from bsu.dependencies import get_service

DB_URL = os.getenv('DB_URL')

user_router = Router()


@user_router.message(CommandStart())
async def start_message(msg: types.Message, session: AsyncSession):
    service = get_service(session)
    user_dto = to_user_dto(msg.from_user)
    user, is_already_exist = await service.get_or_create_user(user_dto)
    if is_already_exist:
        if user.group:
            await msg.answer(
                hello_msg.format(name=msg.from_user.full_name),
                reply_markup=menu
            )
    else:
        await msg.answer(
            hello_msg.format(name=msg.from_user.full_name),
            reply_markup=menu
        )


@user_router.callback_query(F.data == 'back')
async def back_to_menu(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
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
    await state.set_data(msg=callback.message)
    
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
async def insertion_group(msg: types.Message, state: FSMContext, session: AsyncSession):
    service = get_service(session)
    data = await state.get_data()
    main_msg: types.Message = data['msg']
    try:
        group = msg.text.strip()
        msg.delete()
        if len(group) != 8:
            raise WrongFormatGroupNumber
        if not group.isdigit():
            raise WrongFormatGroupNumber
        group_number = int(group)
        await service.add_group_to_user(
            msg.from_user.id,
            group_number
        )
        state.clear()
    except WrongFormatGroupNumber as ex:
        await main_msg.edit_text(
            insert_group_msg_error,
            reply_markup=back_kb
        )
    except Exception as ex:
        await main_msg.edit_text(
            f'{ex}',
            reply_markup=back_kb
        )


@user_router.callback_query(F.data == 'settings')
async def change_settings(callback: types.CallbackQuery, session: AsyncSession):
    service = get_service(session)
    user_dto = to_user_dto(callback.from_user)
    user = await service.get_user_with_settings(user_dto)

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
    user = await service.get_user_with_settings(user_dto)
    user.settings
    current = getattr(user.settings, key)
    setattr(user.settings, key, not current)
    await service.update_settings(user)
    await callback.message.edit_reply_markup(
        reply_markup=get_times_kb(user.settings)
    )
    await callback.answer()
