from typing import List
from enum import Enum
from aiogram import F, Router
from aiogram.filters.callback_data import CallbackData
from aiogram.filters import Command, CommandObject, CommandStart
from bson import ObjectId
from database.services.addresses import AddressesService
from utils import getDate, logger
from database.services.reports import ReportService, Report
from database.services.users import UserService
from filters.status import StatusFilter, UserRole
from texts import MessageText
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery, File
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.models.user import User
from aiogram.enums.parse_mode import ParseMode
from loader import bot
from utils import employeeAccess, getUsername
from utils import getFiltersText
from utils.getButtonsText import filterChange
from utils.getSlice import getSkip
router = Router()

router = Router()

# Получение списка пользовалетей


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


class ReportActions(str, Enum):
    toggleMenuConcact = 'MC'
    toggleMenuFulfilled = 'MF'
    pickPoint = "MP"
    showMenu = "M"
    showReport = "SR"
    toggleReportFulfilled = "RF"
    navigate = "N"
    filters = "F"


class FilterState(int, Enum):
    false = 0
    all = 1
    true = 2


class ReportCallback(CallbackData, prefix="r"):
    action: ReportActions
    contact: FilterState
    fulfilled: FilterState
    point: str
    # Репорт используется только для операции toggleReportFulfilled. Это все. о остальное время можно ставить ""
    report: str
    page: int


maxLimit = 5
# Генерация листа и кнопок. Никакой логики. Дали на вход 5 точек, будет 5 точек, дали 1, будет одна


def drawReports(reports: List[Report], contact: FilterState = FilterState.all, fulfilled: FilterState = FilterState.all, point: str = "", report: str = "", page: int = 1) -> tuple[str, InlineKeyboardMarkup or None]:
    navKeyboard = [
        InlineKeyboardButton(text="Фильтры", callback_data=ReportCallback(action=ReportActions.filters, contact=contact,
                                                                          fulfilled=fulfilled, point=point, report=report, page=page).pack())
    ]
    if not reports:
        return MessageText.noRepotsFound.value, InlineKeyboardMarkup(inline_keyboard=[navKeyboard])

    navKeyboard = [
        InlineKeyboardButton(text="<", callback_data=ReportCallback(action=ReportActions.navigate, contact=contact,
                                                                    fulfilled=fulfilled, point=point, report=report, page=page-1).pack()),
        InlineKeyboardButton(text="Фильтры", callback_data=ReportCallback(action=ReportActions.filters, contact=contact,
                                                                          fulfilled=fulfilled, point=point, report=report, page=page).pack()),
        InlineKeyboardButton(text=">", callback_data=ReportCallback(action=ReportActions.navigate, contact=contact,
                                                                    fulfilled=fulfilled, point=point, report=report, page=page+1).pack()),
    ]

    formatted_list = ""
    keyboard = []
    for i, report in enumerate(reports, start=1):
        report: Report
        emoji = "✅" if report.fulfilled else "❌"
        username = f"@{report.senderUsername}: " if report.contact else ""
        formatted_list += f"{i}. {emoji}: {getDate(report.id)}, {report.shortAddress}\n{username}{report.message}\n\n"
        # Создание кнопки для каждого Report
        keyboard.append(InlineKeyboardButton(text=f"{i}", callback_data=ReportCallback(action=ReportActions.toggleReportFulfilled, contact=contact,
                                                                                       fulfilled=fulfilled, point=point, report=str(report.id), page=page).pack()))

    formatted_list += MessageText.reportNavHelp.value
    keyboard_line = InlineKeyboardMarkup(inline_keyboard=[
        navKeyboard,
        keyboard
    ])
    return formatted_list, keyboard_line


def drawFilters(contact: FilterState, fulfilled: FilterState, point: str, page: int = 1, report: str = ""):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Изм. Связь", callback_data=ReportCallback(action=ReportActions.toggleMenuConcact, contact=contact,
                                 fulfilled=fulfilled, point=point, report=report, page=page).pack()),
            InlineKeyboardButton(text="Изм. Статус", callback_data=ReportCallback(action=ReportActions.toggleMenuFulfilled, contact=contact,
                                 fulfilled=fulfilled, point=point, report=report, page=page).pack()),
        ],
        [
            InlineKeyboardButton(text="Выбрать точку", callback_data=ReportCallback(action=ReportActions.pickPoint, contact=contact,
                                 fulfilled=fulfilled, point=point, report=report, page=page).pack()),
            InlineKeyboardButton(text="Назад", callback_data=ReportCallback(action=ReportActions.navigate, contact=contact,
                                 fulfilled=fulfilled, point=point, report=report, page=page).pack()),
        ]
    ])

# Это первоначальная настройка. Она базовая и не меняется в дальнейшем
@router.message(Command("reports"), StatusFilter(UserRole.ADMIN))
async def showReports(message: Message, **data):
    reports = await ReportService.get_reports_page(limit=maxLimit, skip=getSkip(1, maxLimit))
    list, keyboard = drawReports(reports=reports)

    await message.answer(text=list, reply_markup=keyboard)


@router.callback_query(ReportCallback.filter(F.action == ReportActions.navigate))
async def manageNavigation(query: CallbackQuery, callback_data: ReportCallback, **data):
    if (callback_data.page < 1):
        return await query.answer(MessageText.navFirst.value)
    reports = await ReportService.get_reports_page(limit=maxLimit, skip=getSkip(callback_data.page, maxLimit), address_id=callback_data.point, fulfilled=callback_data.fulfilled, contact=callback_data.contact)
    if not reports and callback_data.page != 1:
        return await query.answer(MessageText.navLast.value)

    # Если данные пришли, то страница существует и данные можно отрисовать
    list, keyboard = drawReports(reports=reports, contact=callback_data.contact, fulfilled=callback_data.fulfilled,
                                 point=callback_data.point, report=callback_data.report, page=callback_data.page)

    # Передаем в клавиатурах измененный стейт. Всегда
    await query.message.edit_text(text=list, reply_markup=keyboard)


@router.callback_query(ReportCallback.filter(F.action == ReportActions.toggleReportFulfilled))
async def toggleReportFulfilled(query: CallbackQuery, callback_data: ReportCallback, **data):
    await ReportService.toggle_fulfilled(callback_data.report)
    reports = await ReportService.get_reports_page(limit=maxLimit, skip=getSkip(callback_data.page, maxLimit), address_id=callback_data.point, fulfilled=callback_data.fulfilled, contact=callback_data.contact)

    list, keyboard = drawReports(reports=reports, contact=callback_data.contact, fulfilled=callback_data.fulfilled,
                                 point=callback_data.point, report=callback_data.report, page=callback_data.page)

    await query.message.edit_text(text=list, reply_markup=keyboard)


@router.callback_query(ReportCallback.filter(F.action == ReportActions.filters))
async def showMenuFilters(query: CallbackQuery, callback_data: ReportCallback, **data):
    filter = await getFiltersText(callback_data.contact, callback_data.fulfilled, callback_data.point)
    keyboard = drawFilters(callback_data.contact,
                           callback_data.fulfilled, callback_data.point)

    await query.message.edit_text(text=filter, reply_markup=keyboard, parse_mode=ParseMode.HTML)


@router.callback_query(ReportCallback.filter(F.action == ReportActions.toggleMenuConcact))
async def showMenuFilters(query: CallbackQuery, callback_data: ReportCallback, **data):
    callback_data.contact = filterChange(callback_data.contact)
    filter = await getFiltersText(callback_data.contact, callback_data.fulfilled, callback_data.point)
    keyboard = drawFilters(callback_data.contact,
                           callback_data.fulfilled, callback_data.point)

    await query.message.edit_text(text=filter, reply_markup=keyboard, parse_mode=ParseMode.HTML)


@router.callback_query(ReportCallback.filter(F.action == ReportActions.toggleMenuFulfilled))
async def showMenuFilters(query: CallbackQuery, callback_data: ReportCallback, **data):
    callback_data.fulfilled = filterChange(callback_data.fulfilled)
    filter = await getFiltersText(callback_data.contact, callback_data.fulfilled, callback_data.point)
    keyboard = drawFilters(callback_data.contact,
                           callback_data.fulfilled, callback_data.point)

    await query.message.edit_text(text=filter, reply_markup=keyboard, parse_mode=ParseMode.HTML)


@router.callback_query(ReportCallback.filter(F.action == ReportActions.pickPoint))
async def showMenuFilters(query: CallbackQuery, callback_data: ReportCallback, **data):
    addresses = await AddressesService.get_addresses()
    text = "Выберите адрес из списка:\n"
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=f"Выбрать все адреса", callback_data=ReportCallback(action=ReportActions.filters, point="",
                             report=callback_data.report, page=callback_data.page, fulfilled=callback_data.fulfilled, contact=callback_data.contact).pack())
    )
    buttons = []
    for i, address in enumerate(addresses, start=1):
        text += f"{i}. {address.address}\n"
        buttons.append(InlineKeyboardButton(text=f"{i}", callback_data=ReportCallback(action=ReportActions.filters, point=str(
            address.id), report=callback_data.report, page=callback_data.page, fulfilled=callback_data.fulfilled, contact=callback_data.contact).pack()))
    builder.row(*buttons, width=5)

    await query.message.edit_text(text=text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)



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
