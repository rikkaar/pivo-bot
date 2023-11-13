from typing import List
from enum import Enum
from aiogram import F, Router
from aiogram.filters.callback_data import CallbackData
from aiogram.filters import Command, CommandObject, CommandStart
from bson import ObjectId
from database.models.requests import Request
from database.services.addresses import AddressesService
from utils import employeeAccess, getDate, getSkip, getUsername, logger
from database.services.reports import ReportService, Report
from database.services.users import UserService
from filters.status import StatusFilter, UserRole
from texts import MessageText
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery, File
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.models.user import User
from aiogram.enums.parse_mode import ParseMode
from loader import bot
import utils
from utils.getButtonsText import filterChange, getFiltersText

router = Router()

@router.message(Command('users'), StatusFilter(UserRole.ADMIN))
async def _users(message: Message):
    text, markup = await _get_users_data()
    await message.answer(text, reply_markup=markup)


# Присвоить пользователю статус работника
@router.message(Command('hire'), StatusFilter(UserRole.ADMIN))
async def hire(message: Message, command: CommandObject):
    if not command.args:
        return await message.answer(MessageText.notEnougthParams.value + MessageText.hireValidationError.value)
    commands = command.args.split()
    if len(commands) != 2:
        return await message.answer(MessageText.notEnougthParams.value + MessageText.hireValidationError.value)
    who, where = commands
    if who.isnumeric():
        who = await UserService.getUserById(who)
    else:
        username = getUsername(who)
        if not username:
            return await message.answer(MessageText.usernameValidationError.value)
        who = await UserService.getUserByUsername(username)

    if not where.isnumeric():
        return await message.answer("Номер точки также должен быть числом!")
    if not who:
        return await message.answer(MessageText.userNotFound.value)
    user: User = await UserService.update_user(who['id'], status=f"{UserRole.EMPLOYEE} {where}")
    await message.answer(f'Теперь {user.username} имеет статус {user.status}')


@router.message(Command('users'), StatusFilter(UserRole.ADMIN))
async def nothing(message: Message, **data):
    # Если мы оказались здесь, то мы либо:
    # SUPER_ADMIN / ADMIN
    # EMPLOYEE 1/2/...
    # Мы имеем доступ к точке 1, если status.split(" ")[1] либо undefined либо равен номеру отображаемой точки. Проверку делает функция employeeAccess
    user: User = data["user"]
    if not employeeAccess(user.status, 1):
        return await message.answer("У вас нет доступа в этой точке")
    await message.answer("Вы имеете доступ к уровню employee и этой точке")


async def _get_users_data():
    users = await UserService.get_users()
    if not users:
        return 'Users is empty', None
    text = ''
    for user in users:
        text += f'\n{"--" * 15}'
        for key, value in user.model_dump().items():
            if key == 'username' and value:
                text += f'\n|{key}: <tg-spoiler><b>@{value}</b></tg-spoiler>'
            else:
                text += f'\n|{key}: <b>{value}</b>'
    return text, None
