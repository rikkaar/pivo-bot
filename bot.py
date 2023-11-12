from utils import logger
from os import getenv
import asyncio
from aiogram import Bot, Dispatcher
from commands import set_default_commands

from handlers import setup_handlers
from middlewares import setup_middlewares

from loader import db, dp, bot

from dotenv import load_dotenv
load_dotenv()

# Функция при запуске бота
# По умолчанию доступны базовые команды


async def on_startup() -> None:
    await set_default_commands()
    logger.info("Bot started!")


async def on_shutdown() -> None:
    # Тут мы можем разорвать соединение с REDIS и c MONGO
    # logger.info("Bot stopped!")
    pass


async def main() -> None:
    setup_middlewares(dp)
    setup_handlers(dp)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    # Не хочу видеть в консоли огромный вывод, когда делаю KeyboardInterrupt
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped with KeyboardInterrupt")
