from enum import Enum
from io import BytesIO
from os import getenv
from aiogram import F, Router
from aiogram.filters.callback_data import CallbackData
from aiogram.filters import Command
from database.services.addresses import AddressesService
from database.services.users import UserService
from texts import MessageText
from utils import generateQrCode, logger, readQR
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery, File
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from database.models.user import User
from database.models.address import Address
from aiogram.enums.parse_mode import ParseMode
from loader import bot
router = Router()


class ProfileActions(str, Enum):
    createQR = 'createQR'
    subscribtions = 'subscribtions'
    stopFSM = 'stopFSM'
    showProfile = 'showProfile'


class ProfileCallback(CallbackData, prefix="profile"):
    action: ProfileActions


profileKeqyboard = InlineKeyboardMarkup(inline_keyboard=[[
    InlineKeyboardButton(text=MessageText.createQRBtn.value, callback_data=ProfileCallback(
        action=ProfileActions.createQR).pack()),
    InlineKeyboardButton(text=MessageText.subscribtionsBtn.value, callback_data=ProfileCallback(
        action=ProfileActions.subscribtions).pack()),
]])


class QR(StatesGroup):
    startMessage = State()
    qr = State()


@router.message(QR.qr, F.text.contains("/") | F.text.in_({"отмена", "назад"}))
async def cancelQRProcess(message: Message, state: FSMContext):
    data = await state.get_data()
    query_id = data.get("startMessage")
    await state.clear()
    await bot.edit_message_text(chat_id=message.from_user.id, message_id=query_id, text=MessageText.createQRcancel.value)


@router.callback_query(ProfileCallback.filter(F.action == ProfileActions.stopFSM))
async def stopQRProcess(query: CallbackQuery, state: FSMContext):
    await state.clear()
    await query.message.edit_text(MessageText.createQRcancel.value)


@router.message(QR.qr, F.text)
async def processQRText(message: Message, state: FSMContext, **data):
    FSMData = await state.get_data()
    query_id = FSMData.get("startMessage")
    await state.clear()

    await bot.edit_message_text(chat_id=message.from_user.id, message_id=query_id, text=f"QR-код успешно обновлен. Номер клиента: {message.text}", reply_markup=None)

    user: User = data["user"]
    text = MessageText.profileMessage.value + f"\n\nВаш статус: {user.status}"
    response = await message.answer_photo(generateQrCode(message.text), caption=text, reply_markup=profileKeqyboard)
    await UserService.update_user(message.from_user.id, qr=response.photo[-1].file_id)


@router.message(QR.qr, F.photo)
async def processQRPhoto(message: Message, state: FSMContext, **data):
    file_id = message.photo[-1].file_id
    file_info: File = await bot.get_file(file_id)
    file: BytesIO = await bot.download_file(file_info.file_path)
    read_res = readQR(file)
    if not read_res:
        return await message.answer(MessageText.createQRphotoError.value)

    FSMData = await state.get_data()
    query_id = FSMData.get("startMessage")
    await state.clear()
    await bot.edit_message_text(chat_id=message.from_user.id, message_id=query_id, text=f"QR-код успешно обновлен. Номер клиента: {read_res}", reply_markup=None)

    user: User = data["user"]
    text = MessageText.profileMessage.value + f"\n\nВаш статус: {user.status}"

    response = await message.answer_photo(generateQrCode(read_res), caption=text, reply_markup=profileKeqyboard)
    await UserService.update_user(message.from_user.id, qr=response.photo[-1].file_id)


@router.message(Command("profile"))
async def showProfile(message: Message, **data):
    user: User = data["user"]

    text = MessageText.profileMessage.value + f"\n\nВаш статус: {user.status}"

    qr_file_id = user.qr
    if qr_file_id:
        return await message.answer_photo(qr_file_id, caption=text, reply_markup=profileKeqyboard)
    else:
        await message.answer(text, reply_markup=profileKeqyboard)


@router.callback_query(ProfileCallback.filter(F.action == ProfileActions.createQR))
async def createQR(query: CallbackQuery, state: FSMContext, **data):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=MessageText.feedbackAbort.value, callback_data=ProfileCallback(
            action=ProfileActions.stopFSM).pack()),
    ]])
    # Входим в FSM и устанавливаем курсор стейта на QR.qr
    await state.set_state(QR.qr)
    result = await query.message.answer(MessageText.createQRhelp.value, reply_markup=keyboard)
    await state.update_data(startMessage=result.message_id)


@router.callback_query(ProfileCallback.filter(F.action == ProfileActions.subscribtions))
async def showSubs(query: CallbackQuery, **data):
    user: User = data['user']
    subs = user.subscribtions
    text = MessageText.yesSubs.value if subs else MessageText.noSubs.value
    for i, sub in enumerate(subs, start=1):
        address: Address = await AddressesService.get_address(str(sub))
        text += f"{i}. {address.address}"

    return await query.message.answer(text=text, reply_markup=None, parse_mode=ParseMode.HTML)
