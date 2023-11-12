from aiogram import Bot, Dispatcher
from motor.motor_asyncio import AsyncIOMotorClient
from aiogram.enums.parse_mode import ParseMode
# Подключаем .env файлы и импортируем функцию getenv()
from os import getenv
from dotenv import load_dotenv
load_dotenv()

# Я пытался делать через HTML, через MDV2, но по итогу пришел к тому, что без парсера - проще всего
bot = Bot(getenv("BOT_TOKEN"))

# Если мы используем редис, он используется вместо MemoryStorage()
if getenv("RD_DB") and getenv("RD_HOST") and getenv("RD_PORT"):
    from aiogram.fsm.storage.redis import RedisStorage
    from redis.asyncio.client import Redis
    storage = RedisStorage(
        Redis(db=getenv("RD_DB"), host=getenv("RD_HOST"), port=getenv("RD_PORT"), password=getenv("RD_PASS")))
else:
    from aiogram.fsm.storage.memory import MemoryStorage
    storage = MemoryStorage()

# Создание диспетчера и указание на storage
dp = Dispatcher(storage=storage)

# Вшиваем в диспетчер клиент для обработки запросов. Он будет доступен в переменной db
client = AsyncIOMotorClient(getenv("MONGO_URL"))
# "bot" - это название базы данных
db = client['bot']
