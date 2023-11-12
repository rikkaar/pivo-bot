from typing import Callable, Dict, Any, Awaitable
from database.models.user import User
from database.services.users import UserService
from utils import logger
from aiogram import BaseMiddleware
from aiogram.types import Update
from commands import updateCommands


# Этот мидлварь нужен, чтобы получать актуальную роль пользователя при каждом его обращении к боту
# Отправляется запрос к mongoDB
# Нам важно знать id, возможно username (для удобства) и роль. Можно разгрузить трафик, доставая только три поля, вместо всех. Но это потом
# А зочем получать про id/username/name из БД, если оно прикрепляется к любому сообщению?
# Мы должны обращаться к бд только за ролью и только, если эта роль важна. ТОЛЬКО ЕСЛИ РОЛЬ ВАЖНА!

class UserMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any],
    ) -> Any:
        if event.message:
            from_user = event.message.from_user
        if event.callback_query:
            from_user = event.callback_query.from_user
        if event.inline_query:
            from_user = event.inline_query.from_user
        user: User = await UserService.get_or_create_user(from_user.id, name=from_user.full_name, username=from_user.username.lower())
        await updateCommands(user)
        data['user'] = user
        return await handler(event, data)
