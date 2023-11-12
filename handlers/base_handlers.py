from enum import Enum
from aiogram import Router, types
from bson import ObjectId
from database.models.user import User
from database.services.addresses import AddressesService
from database.services.users import UserService
from filters.status import UserRole
import random
from aiogram import F
from aiogram.types import Message
from aiogram.filters import Command, CommandObject, CommandStart
from texts import MessageText
from utils import generateQrCode, logger
from filters import StatusFilter
from aiogram.utils.formatting import Bold, Text, as_list
from keyboards import builders, inline, reply

router = Router()

# Обновление своего статуса можно сделать с помощью перехода в
# @router.message(Command())
# async def loadCommands
# Информация о пользователе попадает в БД при команде /start


@router.message(CommandStart())
async def start(message: Message) -> None:
    content = Text(
        "Привет, ", Bold(message.from_user.full_name)
    )
    return await message.answer(**content.as_kwargs())


@router.message(Command("getUser"))
async def getFullUserInfo(message: Message, command: CommandObject):
    if not command.args:
        return await message.answer(**as_list(Text("Ошибка: Передайте Id пользователя"), Text("Пример: /getUser <Id>")).as_kwargs())
    if not command.args.isnumeric():
        return await message.answer("Эта функция работает только с числами!")
    user = await UserService.getUserById(command.args)
    await message.answer(f"Вот username пользователя с id {command.args}: @{user.username}")


@router.message(Command("createAddresses"), StatusFilter(UserRole.ADMIN))
async def createAddresse(message: Message):
    await AddressesService.create_address(address="Нижний Новгород, пр-кт Гагарина,  д.182", lat=56.240603, lon=43.963478)
    await AddressesService.create_address(address="Нижний Новгород, ул. Костина д.13", lat=56.309039, lon=43.990985)
    await message.answer("Two addresses added\.\.")


@router.message(Command("genConfig"), StatusFilter(UserRole.ADMIN))
async def genConfig(message: Message):
    await AddressesService.generateConfig()
    await message.answer("Config generated")


@router.message(Command('hire'))
@router.message(Command('users'))
async def nothing(message: Message):
    await message.answer("У вас нет доступа к этой команде :(")

@router.message(F.text)
async def echo(message: Message):
    msg = message.text.lower()

    if msg == "ссылки":
        await message.answer("Вот ваши ссылки:", reply_markup=inline.links)
    elif msg == "спец. кнопки":
        await message.answer("Спец. кнопки:", reply_markup=reply.spec)
    elif msg == "калькулятор":
        await message.answer("Введите выражение:", reply_markup=builders.calc())
    elif msg == "назад":
        await message.answer("Вы перешли в главное меню!", reply_markup=reply.main)
    else:
        await message.answer("Я тебя не понял :(")
