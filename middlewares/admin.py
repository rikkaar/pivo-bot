from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message

from commands import set_admins_commands
from database.models.user import User
from filters.status import UserRole

class AdminMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any],
    ) -> Any:
        user: User = data['user']
        if user.status in (UserRole.ADMIN.name, UserRole.SUPER_ADMIN.name):
            await set_admins_commands(user.id)
        return await handler(event, data)
