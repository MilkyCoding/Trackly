from aiogram import Dispatcher

from src.bot.handlers.admin import register_admin_handlers
from src.bot.handlers.other import register_other_handlers
from src.bot.handlers.user.main import register_user_handlers


def register_all_handlers(dp: Dispatcher) -> None:
    handlers = (
        register_user_handlers,
        register_admin_handlers,
        register_other_handlers,
    )
    for handler in handlers:
        handler(dp)
