from database.models.user import User
from filters.status import UserRole

from .admins import set_admins_commands
from .default import set_default_commands_for_user, set_default_commands
from .employee import set_employee_commands


async def updateCommands(user: User) -> None:
    if (user.status in [UserRole.ADMIN.name, UserRole.SUPER_ADMIN.name]):
        await set_admins_commands(user.id)
    elif (UserRole.EMPLOYEE.name in user.status):
        await set_employee_commands(user.id)
    else:
        await set_default_commands_for_user(user.id)
