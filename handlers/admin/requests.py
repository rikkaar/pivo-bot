from typing import List
from enum import Enum
from aiogram import F, Router
from aiogram.filters.callback_data import CallbackData
from aiogram.filters import Command, CommandObject, CommandStart
from bson import ObjectId
from database.models.requests import Request
from database.services.addresses import AddressesService
from utils import employeeAccess, getDate, getSkip, getUsername, logger
from database.services.requests import RequestService, Request
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
from aiogram.utils.formatting import Text

router = Router()
maxLimit = 5

class RequestActions(str, Enum):
    toggleMenuConcact = 'MC'
    toggleMenuFulfilled = 'MF'
    pickPoint = "MP"
    showMenu = "M"
    showRequest = "SR"
    toggleRequestFulfilled = "RF"
    navigate = "N"
    filters = "F"


class FilterState(int, Enum):
    false = 0
    all = 1
    true = 2


class RequestCallback(CallbackData, prefix="rq"):
    action: RequestActions
    contact: FilterState
    fulfilled: FilterState
    point: str
    # Репорт используется только для операции toggleRequestFulfilled. Это все. о остальное время можно ставить ""
    request: str
    page: int

def drawRequests(requests: List[Request], contact: FilterState = FilterState.all, fulfilled: FilterState = FilterState.all, point: str = "", request: str = "", page: int = 1) -> tuple[str, InlineKeyboardMarkup or None]:
    navKeyboard = [
        InlineKeyboardButton(text="Фильтры", callback_data=RequestCallback(action=RequestActions.filters, contact=contact,
                                                                          fulfilled=fulfilled, point=point, request=request, page=page).pack())
    ]
    if not requests:
        return MessageText.noRepotsFound.value, InlineKeyboardMarkup(inline_keyboard=[navKeyboard])

    navKeyboard = [
        InlineKeyboardButton(text="<", callback_data=RequestCallback(action=RequestActions.navigate, contact=contact,
                                                                    fulfilled=fulfilled, point=point, request=request, page=page-1).pack()),
        InlineKeyboardButton(text="Фильтры", callback_data=RequestCallback(action=RequestActions.filters, contact=contact,
                                                                          fulfilled=fulfilled, point=point, request=request, page=page).pack()),
        InlineKeyboardButton(text=">", callback_data=RequestCallback(action=RequestActions.navigate, contact=contact,
                                                                    fulfilled=fulfilled, point=point, request=request, page=page+1).pack()),
    ]

    formatted_list = ""
    keyboard = []
    for i, request in enumerate(requests, start=1):
        request: Request
        emoji = "✅" if request.fulfilled else "❌"
        username = f"@{Text(request.senderUsername).as_html()}: " if request.contact else "Anon: "
        formatted_list += f"{i}. {emoji}: {getDate(request.id)}, {request.shortAddress}, {username}\n{request.name} - <a href='{request.link}'>ссылка</a>\n\n"
        # Создание кнопки для каждого Request
        keyboard.append(InlineKeyboardButton(text=f"{i}", callback_data=RequestCallback(action=RequestActions.toggleRequestFulfilled, contact=contact,
                                                                                       fulfilled=fulfilled, point=point, request=str(request.id), page=page).pack()))

    formatted_list += MessageText.reportNavHelp.value
    keyboard_line = InlineKeyboardMarkup(inline_keyboard=[
        navKeyboard,
        keyboard
    ])
    return formatted_list, keyboard_line

def drawFilters(contact: FilterState, fulfilled: FilterState, point: str, page: int = 1, request: str = ""):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Изм. Связь", callback_data=RequestCallback(action=RequestActions.toggleMenuConcact, contact=contact,
                                 fulfilled=fulfilled, point=point, request=request, page=page).pack()),
            InlineKeyboardButton(text="Изм. Статус", callback_data=RequestCallback(action=RequestActions.toggleMenuFulfilled, contact=contact,
                                 fulfilled=fulfilled, point=point, request=request, page=page).pack()),
        ],
        [
            InlineKeyboardButton(text="Выбрать точку", callback_data=RequestCallback(action=RequestActions.pickPoint, contact=contact,
                                 fulfilled=fulfilled, point=point, request=request, page=page).pack()),
            InlineKeyboardButton(text="Назад", callback_data=RequestCallback(action=RequestActions.navigate, contact=contact,
                                 fulfilled=fulfilled, point=point, request=request, page=page).pack()),
        ]
    ])


# Это первоначальная настройка. Она базовая и не меняется в дальнейшем
@router.message(Command("requests"), StatusFilter(UserRole.ADMIN))
async def showReports(message: Message, **data):
    requests = await RequestService.get_requests_page(limit=maxLimit, skip=utils.getSkip(1, maxLimit))
    list, keyboard = drawRequests(requests=requests)

    await message.answer(text=list, reply_markup=keyboard, parse_mode=ParseMode.HTML, disable_web_page_preview=True)


@router.callback_query(RequestCallback.filter(F.action == RequestActions.navigate))
async def manageNavigation(query: CallbackQuery, callback_data: RequestCallback, **data):
    if (callback_data.page < 1):
        return await query.answer(MessageText.navFirst.value)
    requests = await RequestService.get_requests_page(limit=maxLimit, skip=getSkip(callback_data.page, maxLimit), address_id=callback_data.point, fulfilled=callback_data.fulfilled, contact=callback_data.contact)
    if not requests and callback_data.page != 1:
        return await query.answer(MessageText.navLast.value)

    # Если данные пришли, то страница существует и данные можно отрисовать
    list, keyboard = drawRequests(requests=requests, contact=callback_data.contact, fulfilled=callback_data.fulfilled,
                                 point=callback_data.point, request=callback_data.request, page=callback_data.page)

    # Передаем в клавиатурах измененный стейт. Всегда
    await query.message.edit_text(text=list, reply_markup=keyboard, parse_mode=ParseMode.HTML, disable_web_page_preview=True)


@router.callback_query(RequestCallback.filter(F.action == RequestActions.toggleRequestFulfilled))
async def toggleRequestFulfilled(query: CallbackQuery, callback_data: RequestCallback, **data):
    RequestService
    await RequestService.toggle_fulfilled(callback_data.request)
    
    requests = await RequestService.get_requests_page(limit=maxLimit, skip=getSkip(callback_data.page, maxLimit), address_id=callback_data.point, fulfilled=callback_data.fulfilled, contact=callback_data.contact)

    list, keyboard = drawRequests(requests=requests, contact=callback_data.contact, fulfilled=callback_data.fulfilled,
                                 point=callback_data.point, request=callback_data.request, page=callback_data.page)

    await query.message.edit_text(text=list, reply_markup=keyboard, parse_mode=ParseMode.HTML, disable_web_page_preview=True)


@router.callback_query(RequestCallback.filter(F.action == RequestActions.filters))
async def showMenuFilters(query: CallbackQuery, callback_data: RequestCallback, **data):
    filter = await getFiltersText(callback_data.contact, callback_data.fulfilled, callback_data.point)
    keyboard = drawFilters(callback_data.contact,
                           callback_data.fulfilled, callback_data.point)

    await query.message.edit_text(text=filter, reply_markup=keyboard, parse_mode=ParseMode.HTML)


@router.callback_query(RequestCallback.filter(F.action == RequestActions.toggleMenuConcact))
async def showMenuFilters(query: CallbackQuery, callback_data: RequestCallback, **data):
    callback_data.contact = filterChange(callback_data.contact)
    filter = await getFiltersText(callback_data.contact, callback_data.fulfilled, callback_data.point)
    keyboard = drawFilters(callback_data.contact,
                           callback_data.fulfilled, callback_data.point)

    await query.message.edit_text(text=filter, reply_markup=keyboard, parse_mode=ParseMode.HTML)


@router.callback_query(RequestCallback.filter(F.action == RequestActions.toggleMenuFulfilled))
async def showMenuFilters(query: CallbackQuery, callback_data: RequestCallback, **data):
    callback_data.fulfilled = filterChange(callback_data.fulfilled)
    filter = await getFiltersText(callback_data.contact, callback_data.fulfilled, callback_data.point)
    keyboard = drawFilters(callback_data.contact,
                           callback_data.fulfilled, callback_data.point)

    await query.message.edit_text(text=filter, reply_markup=keyboard, parse_mode=ParseMode.HTML)


@router.callback_query(RequestCallback.filter(F.action == RequestActions.pickPoint))
async def showMenuFilters(query: CallbackQuery, callback_data: RequestCallback, **data):
    addresses = await AddressesService.get_addresses()
    text = "Выберите адрес из списка:\n"
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=f"Выбрать все адреса", callback_data=RequestCallback(action=RequestActions.filters, point="",
                             request=callback_data.request, page=callback_data.page, fulfilled=callback_data.fulfilled, contact=callback_data.contact).pack())
    )
    buttons = []
    for i, address in enumerate(addresses, start=1):
        text += f"{i}. {address.address}\n"
        buttons.append(InlineKeyboardButton(text=f"{i}", callback_data=RequestCallback(action=RequestActions.filters, point=str(
            address.id), request=callback_data.request, page=callback_data.page, fulfilled=callback_data.fulfilled, contact=callback_data.contact).pack()))
    builder.row(*buttons, width=5)

    await query.message.edit_text(text=text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)