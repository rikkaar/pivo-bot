from aiogram.types import BotCommand, BotCommandScopeChat

from loader import bot
from .default import get_default_commands

# вывести список кранов - (выбрать точку) - не давать доступ к этой команды вне контекста выбора точки. Вывести в точке кнопку
# /taps <where> -- для обычных пользователей просмотр
# /tap 1-1 (какой кран и какая позиция на кране)
# /update_tap 1-1 (какой кран и какая позиция) - сюда можно подключить FSM
# Выпадет контекстное меню: заменить, в стоп-лист

def get_employee_commands():
    commands = get_default_commands()
    commands.extend([
        BotCommand(command='/update_tap', description='Изменить состояние на кранах')
    ])
    return commands


async def set_employee_commands(id: int):
    await bot.set_my_commands(get_employee_commands(), scope=BotCommandScopeChat(chat_id=id))