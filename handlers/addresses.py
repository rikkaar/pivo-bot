from enum import Enum
import re
from aiogram import F, Router
from aiogram.filters.callback_data import CallbackData
from aiogram.filters import Command, CommandObject
from database.services.addresses import AddressesService
from database.services.reports import ReportService
from database.services.requests import RequestService
from database.services.users import UserService
from texts import MessageText
from utils import logger
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from database.models.user import User
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from loader import bot
router = Router()


class AddressesActions(str, Enum):
    newAddress = 'newAddress'
    back = 'back'
    subscribe = 'subscribe'
    showCraft = 'showCraft'
    showTaps = 'showTaps'
    request = 'request'
    report = 'report'
    stopFSM = 'stopFSM'


class AddressCallback(CallbackData, prefix="Add"):
    action: AddressesActions
    addressId: str

#
# СПИСОК адресов
#


def drawaKeyboard(addressId: str, subBtnText: MessageText, lat: int, lon: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Крафт", callback_data=AddressCallback(
                action=AddressesActions.showCraft, addressId=addressId).pack()),
            InlineKeyboardButton(text="Краны", callback_data=AddressCallback(
                action=AddressesActions.showTaps, addressId=addressId).pack()),
        ],
        [
            InlineKeyboardButton(text="Запрос на поставку", callback_data=AddressCallback(
                action=AddressesActions.request, addressId=addressId).pack()),
            InlineKeyboardButton(text="Отправить репорт", callback_data=AddressCallback(
                action=AddressesActions.report, addressId=addressId).pack()),
        ],
        [
            InlineKeyboardButton(text="Местоположение", callback_data=CoordsCallback(
                lat=lat, lon=lon).pack()),
            InlineKeyboardButton(text=subBtnText.value, callback_data=AddressCallback(
                action=AddressesActions.subscribe, addressId=addressId).pack()),
        ]
    ])

@router.message(Command("addresses"))
async def showAddresses(message: Message):
    addresses = await AddressesService.get_addresses()
    text = MessageText.pickPointMap.value
    buttons = []

    config = await AddressesService.getMapConfig()
    if not config:
        config = await AddressesService.generateMapConfig()

    for i, address in enumerate(addresses, start=1):
        text += f"{i}. {address.address}\n"
        buttons.append(InlineKeyboardButton(text=f"{i}", callback_data=AddressCallback(
            action=AddressesActions.newAddress, addressId=str(address.id)).pack()))
    keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])
    # await message.answer(text, reply_markup=keyboard)

    text += MessageText.pickPointHelp.value
    response = await message.answer_photo(config.map, caption=text, reply_markup=keyboard)
    if "https://static-maps.yandex.ru" in config.map:
        await AddressesService.updateMapConfig(response.photo[-1].file_id)


#
# ОТКРЫТЬ новое сообщение о магазине
#

# Сдесь фильтрация по action=newAddress. потом можно для edit сделать фильтрацию по editAddress
@router.callback_query(AddressCallback.filter(F.action == AddressesActions.newAddress))
async def showAddress(query: CallbackQuery, callback_data: AddressCallback, **data) -> None:
    address = await AddressesService.get_address(callback_data.addressId)
    user: User = data["user"]

    isSubscribed = callback_data.addressId in user.subscribtions
    subBtnText = MessageText.unsubscribe if isSubscribed else MessageText.subscribe
    keyboard = drawaKeyboard(callback_data.addressId, subBtnText, address.lat, address.lon)

    await query.message.answer(text=address.address, reply_markup=keyboard)


#
# РЕДАКТИРОВАТЬ сообщение о магазине
#

@router.callback_query(AddressCallback.filter(F.action == AddressesActions.back))
async def showAddressEdited(query: CallbackQuery, callback_data: AddressCallback, **data) -> None:
    address = await AddressesService.get_address(callback_data.addressId)
    user: User = data["user"]

    isSubscribed = callback_data.addressId in user.subscribtions
    subBtnText = MessageText.unsubscribe if isSubscribed else MessageText.subscribe
    keyboard = drawaKeyboard(callback_data.addressId, subBtnText, address.lat, address.lon)


    await query.message.edit_text(text=address.address, reply_markup=keyboard)


#
# КНОПКА подписаться/отписаться
#

@router.callback_query(AddressCallback.filter(F.action == AddressesActions.subscribe))
async def subscribeToPoint(query: CallbackQuery, callback_data: AddressCallback, **data) -> None:
    address = await AddressesService.get_address(callback_data.addressId)
    user: User = data["user"]
    isSubscribed = await UserService.subscribe(user.id, callback_data.addressId, user.subscribtions)

    subBtnText = MessageText.unsubscribe if isSubscribed else MessageText.subscribe
    keyboard = drawaKeyboard(callback_data.addressId, subBtnText, address.lat, address.lon)

    await query.message.edit_reply_markup(reply_markup=keyboard)


#
# КНОПКА список крафта
#

@router.callback_query(AddressCallback.filter(F.action == AddressesActions.showCraft))
async def subscribeToPoint(query: CallbackQuery, callback_data: AddressCallback, **data) -> None:
    address = await AddressesService.get_address(callback_data.addressId)
    user: User = data["user"]

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Назад", callback_data=AddressCallback(
            action=AddressesActions.back, addressId=callback_data.addressId).pack())
    ]])
    await query.message.edit_text(text="Актуальный крафт", reply_markup=keyboard)


#
# КНОПКА список крафта
#

@router.callback_query(AddressCallback.filter(F.action == AddressesActions.showTaps))
async def subscribeToPoint(query: CallbackQuery, callback_data: AddressCallback, **data) -> None:
    address = await AddressesService.get_address(callback_data.addressId)
    user: User = data["user"]

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Назад", callback_data=AddressCallback(
            action=AddressesActions.back, addressId=callback_data.addressId).pack())
    ]])
    await query.message.edit_text(text="Что на кранах", reply_markup=keyboard)


#
# КНОПКА отправить репорт
#

class Report(StatesGroup):
    startMessage = State()
    address: State()
    message = State()
    contact = State()


@router.callback_query(AddressCallback.filter(F.action == AddressesActions.stopFSM))
async def stopFSMProcess(query: CallbackQuery, state: FSMContext):
    await state.clear()
    # await query.message.delete()
    await query.message.edit_text(text="Вы прервали заполнение формы")

@router.callback_query(AddressCallback.filter(F.action == AddressesActions.report))
async def reportProcess(query: CallbackQuery, callback_data: AddressCallback, state: FSMContext, **data) -> None:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=MessageText.feedbackAbort.value, callback_data=AddressCallback(
            action=AddressesActions.stopFSM, addressId=callback_data.addressId).pack())
    ]])
    await state.set_state(Report.message)
    await state.update_data(address=callback_data.addressId)
    result = await query.message.answer(text=MessageText.reportMessage.value, reply_markup=keyboard)
    await state.update_data(startMessage=result.message_id)

contact_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Да"),
            KeyboardButton(text="Нет")
        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder="Выберите действие из меню",
    selective=True
)

@router.message(Report.message, F.text)
async def processReportText(message: Message, state: FSMContext):
    await state.update_data(message=message.text)
    await state.set_state(Report.contact)

    await message.answer(MessageText.shouldContact.value, reply_markup=contact_keyboard)


@router.message(Report.message, ~F.text)
async def processReportText(message: Message):
    await message.answer(MessageText.textError.value)


@router.message(Report.contact, F.text.lower().in_({"да", "нет"}))
async def processReportText(message: Message, state: FSMContext, **data):
    await state.update_data(contact=True if message.text.lower() == "да" else False)
    FSMdata = await state.get_data()
    await state.clear()
    user: User = data['user']
    address = await AddressesService.get_address(FSMdata['address'])
    report = await ReportService.create_report(
        address=address.id,
        shortAddress=address.shortAddress,
        sender=user.id,
        message=FSMdata['message'],
        contact=FSMdata['contact'],
        senderUsername=user.username,
    ) 

    if FSMdata['contact']:
        await message.answer(MessageText.reportSentWithFeedback.value, reply_markup=ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
    else:
        await message.answer(MessageText.reportSent.value, reply_markup=ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
    await bot.edit_message_text(text=f"Репорт {str(report.id)}:", chat_id=user.id, message_id=FSMdata['startMessage'], reply_markup=None)


@router.message(Report.contact, ~F.text.lower().in_({"да", "нет"}))
async def processReportText(message: Message):
    await message.answer(MessageText.shouldContactError.value)


#
# КНОПКА Запрос на поставку
#

class Request(StatesGroup):
    startMessage = State()
    address: State()
    name = State()
    link = State()
    contact = State()


@router.callback_query(AddressCallback.filter(F.action == AddressesActions.request))
async def reportProcess(query: CallbackQuery, callback_data: AddressCallback, state: FSMContext) -> None:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=MessageText.feedbackAbort.value, callback_data=AddressCallback(
            action=AddressesActions.stopFSM, addressId=callback_data.addressId).pack())
    ]])
    await state.set_state(Request.name)
    await state.update_data(address=callback_data.addressId)
    result = await query.message.answer(text=MessageText.requestMessage.value, reply_markup=keyboard)
    await state.update_data(startMessage=result.message_id)



@router.message(Request.name, F.text)
async def processReportText(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Request.link)

    await message.answer(MessageText.requestLink.value, parse_mode=ParseMode.HTML)


@router.message(Request.name, ~F.text)
async def processReportText(message: Message):
    await message.answer(MessageText.textError.value)


@router.message(Request.link, F.text.regexp(r'[(http(s)?):\/\/(www\.)?a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)', flags=re.IGNORECASE))
async def processReportText(message: Message, state: FSMContext):
    await state.update_data(link=message.text)
    await state.set_state(Request.contact)

    await message.answer(MessageText.shouldContact.value, reply_markup=contact_keyboard)

@router.message(Request.link)
async def processReportText(message: Message):
    await message.answer(MessageText.requestLinkError.value)


@router.message(Request.contact, F.text.lower().in_({"да", "нет"}))
async def processReportText(message: Message, state: FSMContext, **data):
    await state.update_data(contact=True if message.text.lower() == "да" else False)
    FSMdata = await state.get_data()
    await state.clear()
    user: User = data['user']
    address = await AddressesService.get_address(FSMdata['address'])
    request = await RequestService.create_request(
        address_id=address.id,
        shortAddress=address.shortAddress,
        sender=user.id,
        senderUsername=user.username,
        name=FSMdata['name'],
        link=FSMdata['link'],
        contact=FSMdata['contact'],
    ) 

    if FSMdata['contact']:
        await message.answer(MessageText.requestSentWithFeedback.value, reply_markup=ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
    else:
        await message.answer(MessageText.requestSent.value, reply_markup=ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
    await bot.edit_message_text(text=f"Запрос на поставку {str(request.id)}:", chat_id=user.id, message_id=FSMdata['startMessage'], reply_markup=None)


@router.message(Request.contact, ~F.text.lower().in_({"да", "нет"}))
async def processReportText(message: Message):
    await message.answer(MessageText.shouldContactError.value)



#
# КНОПКА отправить локацию
#

class CoordsCallback(CallbackData, prefix="coords"):
    lat: float
    lon: float


@router.callback_query(CoordsCallback.filter())
async def sendCoords(query: CallbackQuery, callback_data: CoordsCallback) -> None:
    await query.message.answer_location(latitude=callback_data.lat, longitude=callback_data.lon)
