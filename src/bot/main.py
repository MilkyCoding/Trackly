import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

from src.bot.misc import TgKeys
from src.bot.handlers import router
from src.bot.database.models import register_models
from src.bot.services.price_checker import PriceChecker

async def __on_start_up(bot: Bot) -> None:
    # Удаляем все обновления при запуске
    await bot.delete_webhook(drop_pending_updates=True)
    
    register_models()
    
    # Start price checker
    price_checker = PriceChecker(bot)
    asyncio.create_task(price_checker.start())

async def main():
    logging.basicConfig(level=logging.INFO)
    
    bot = Bot(
        token=TgKeys.TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())
    
    # Register handlers
    dp.include_router(router)
    
    # Start bot
    await __on_start_up(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
