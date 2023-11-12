from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat

from loader import bot


def get_default_commands():
    commands = [
        # BotCommand(command='/start', description='Начать работу с ботом'),
        # BotCommand(command="/about", description="Об этом боте"),
        BotCommand(command="/profile", description="Ваш профиль"),
        BotCommand(command="/addresses", description="Список наших адресов"),
        BotCommand(command="/search", description="Поиск пыва"),
    ]
    return commands


async def set_default_commands():
    await bot.set_my_commands(get_default_commands(), scope=BotCommandScopeDefault())

async def set_default_commands_for_user(id: int):
    await bot.set_my_commands(get_default_commands(), scope=BotCommandScopeChat(chat_id=id))
