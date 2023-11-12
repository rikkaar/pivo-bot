from bson import ObjectId
from loader import bot
from pymongo import ReturnDocument

from filters import UserRole
from ..models import User, users_collection
from utils import logger


class UserService():
    @staticmethod
    async def get_users() -> list[User]:
        users = users_collection.find()
        return [User(**u) async for u in users]

    async def get_user(id: int) -> User or None:
        user = await users_collection.find_one({'id': id})
        return User(**user) if user else None

    async def create_user(id: int, **kwargs) -> User:
        # Это дефолтный статус. Его можно изменить либо имея права админа через команду, либо прямо в БД
        kwargs['status'] = UserRole.USER.name
        _id = await users_collection.insert_one({'id': id, **kwargs})
        user = await users_collection.find_one({"_id": _id.inserted_id})
        return User(**user)

    async def update_user(id: int, **kwargs) -> User:
        user = await users_collection.find_one_and_update({'id': id}, {'$set': kwargs}, return_document=ReturnDocument.AFTER)
        return User(**user)

    async def get_or_create_user(id: int, **kwargs) -> User:
        # Мы всегда будем считать, что в БД содержится актуальная информация статуса, id - статичен
        # Может меняться name и username, но это незначительная информация?
        isUserExists = await UserService.get_user(id)
        user = await UserService.update_user(id, **kwargs) if isUserExists else await UserService.create_user(id, **kwargs)
        return user

    async def getUserByUsername(username: str) -> User:
        return await users_collection.find_one({"username": username})

    async def getUserById(id: int) -> User or None:
        try:
            return await bot.get_chat(id)
        except:
            return None

    async def subscribe(id: int, addressId: str, subs: list[ObjectId]) -> True or False:
        if addressId in subs:
            subs.remove(addressId)
            isSubscribed = False
        else:
            subs.append(addressId)
            isSubscribed = True

        await UserService.update_user(id, subscribtions=subs)
        return isSubscribed
