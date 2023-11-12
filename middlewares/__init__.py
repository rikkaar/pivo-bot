from aiogram import Dispatcher
from .user import UserMiddleware

# Мидлварь можно повесить на весь диспетчер
# Мидлварь можно повесить на конкретный роутер, чтобы лишний раз не заходить в цепочку

# Для сотрудников будет отдельный мидлварь на их отдельном роутере. Он будет проверять их принадлежность к точке
# и давать доступ только к изменениям внтури точки

# Для добавления команд использовать мидлварь для каждой роли сомнительная идея. Я бы использовал один мидлварь
# вроде "SetCommandsMiddleware" и он бы уже ставил нужные клавиатуры в зависимости от роли
# Сейчас я просто запихнул updateCommands() в UserMiddleware()


def setup_middlewares(dp: Dispatcher) -> None:
    dp.update.middleware(UserMiddleware())
    # admin_router.message.middleware(AdminMiddleware())
    # employee_router.message.middleware(EmployeeMiddleware())
