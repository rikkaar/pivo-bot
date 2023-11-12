from enum import Enum
from io import BytesIO
from aiogram import F, Router
from aiogram.filters.callback_data import CallbackData
from aiogram.filters import Command, CommandObject, CommandStart
from texts import MessageText
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery, File
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from database.models.user import User
from aiogram.enums.parse_mode import ParseMode
from loader import bot
from utils import readBarcode
router = Router()


# Поиск можно делать либо по названию, либо по тексту штришкода, либо по фотке штрихкода

class SearchActions(str, Enum):
    barcode = 'barcode'
    input = 'input'
    stopFSM = 'stopFSM'
    srartFSM = 'startFSM'


class SearchCallback(CallbackData, prefix="search"):
    action: SearchActions
    # id: int


class Search(StatesGroup):
    startMessage = State()
    query = State()


@router.message(Command("search"))
async def searchMenuStart(message: Message, state: FSMContext, **data):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Покинуть поиск", callback_data=SearchCallback(
            action=SearchActions.stopFSM).pack()),
    ]])
    await state.set_state(Search.query)
    result = await message.answer(text=MessageText.searchHelp.value, reply_markup=keyboard)
    await state.update_data(startMessage=result.message_id)


@router.callback_query(SearchCallback.filter(F.action == SearchActions.stopFSM))
async def searchMenuStop(query: CallbackQuery, callback_data: CallbackData, state: FSMContext, **data):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Начать новый поиск", callback_data=SearchCallback(
            action=SearchActions.srartFSM).pack()),
    ]])
    await state.clear()
    await query.message.edit_text(text=MessageText.searchCancel.value, reply_markup=keyboard)


@router.callback_query(SearchCallback.filter(F.action == SearchActions.srartFSM))
async def searchMenuAgain(query: CallbackQuery, callback_data: CallbackData, state: FSMContext, **data):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Покинуть поиск", callback_data=SearchCallback(
            action=SearchActions.stopFSM).pack()),
    ]])
    await state.set_state(Search.query)
    if query.message.text == MessageText.searchCancel.value:
        result = await query.message.edit_text(text=MessageText.searchHelp.value, reply_markup=keyboard)
    else:
        result = await query.message.answer(text=MessageText.searchHelp.value, reply_markup=keyboard)
    await state.update_data(startMessage=result.message_id)


@router.message(Search.query, F.text)
async def searchByBarcode(message: Message, state: FSMContext):
    FSMData = await state.get_data()
    msg_id = FSMData.get("startMessage")
    await state.clear()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Начать новый поиск", callback_data=SearchCallback(
            action=SearchActions.srartFSM).pack()),
    ]])
    # Пока не буду делать разделение логики по тому, что мы ищем, баркод или название

    # получение поиска сложно
    search_result = "Результат поиска"
    await message.answer(text=search_result, parse_mode=ParseMode.HTML)
    # тут можно изменить еще и текст, чтобы сообщение было вроде: "Вы искали"
    await bot.edit_message_text(chat_id=message.from_user.id, message_id=msg_id, text=f"Ваш поисковой запрос: {message.text}", reply_markup=keyboard)


@router.message(Search.query, F.photo)
async def searchByPhoto(message: Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    file_info: File = await bot.get_file(file_id)
    file: BytesIO = await bot.download_file(file_info.file_path)
    read_res = readBarcode(file)
    if not read_res:
        return await message.answer(MessageText.searchPhotoError.value)


    FSMData = await state.get_data()
    msg_id = FSMData.get("startMessage")
    await state.clear()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Начать новый поиск", callback_data=SearchCallback(
            action=SearchActions.srartFSM).pack()),
    ]])
    # Пока не буду делать разделение логики по тому, что мы ищем, баркод или название

    # получение поиска сложно
    search_result = "Результат поиска"
    await message.answer(text=search_result, parse_mode=ParseMode.HTML)
    # тут можно изменить еще и текст, чтобы сообщение было вроде: "Вы искали"
    await bot.edit_message_text(chat_id=message.from_user.id, message_id=msg_id, text=f"Ваш поисковой запрос: {read_res}", reply_markup=keyboard)
