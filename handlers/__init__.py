from aiogram import Dispatcher


from .admin_handlers import router as admin_router
from .employee_handlers import router as employee_router
from .base_handlers import router as base_router
from .profile import router as profile_router
from .search import router as search_router
from .addresses import router as addresses_router


def setup_handlers(dp: Dispatcher) -> None:
    dp.include_routers(admin_router, employee_router, profile_router, search_router, addresses_router, base_router)
