from enum import Enum
from aiogram.filters import Filter
from aiogram.types import Message
from database.models.user import User
from utils import logger


# Здесь мы проверяем, может ли человек вообще воспользоваться командой. Если нет, то мы говорим ему о том, что у него нет прав
#  и обновляем клавиатуру в соответсвии с его ролью.
# Если права есть, то позволяем вызов функции не обрывается здесь и утекает дальше

# Хуевая идея использовать фильтрацию для ограничения доступа. Если команда имеет несколько отображений для разных ролей,
# то у нас появляется несколько выводов.

# В данном виде обработка только в иерархии admins, но проще получать простой вывод по сравнению без дополнительного вывода.
# А как для employee <номер точки>? Будем это уже парсить внутри функции, но у админа не будет указания точки...

class UserRole(Enum):
    SUPER_ADMIN = 0
    ADMIN = 1
    EMPLOYEE = 2
    USER = 3

    def __str__(self):
        return self._name_


class StatusFilter(Filter):
    def __init__(self, status: UserRole) -> None:
        self.status = status
        self.statuses = [UserRole.SUPER_ADMIN.name, UserRole.ADMIN.name,
                         UserRole.EMPLOYEE.name, UserRole.USER.name]

    async def __call__(self, message: Message, **data: dict) -> bool:
        user: User = data['user']
        user_status = user.status.split(" ")[0]
        return self.statuses.index(user_status) <= self.status.value
