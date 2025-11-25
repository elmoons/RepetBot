import asyncio
import logging
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

sys.path.append(str(Path(__file__).parent.parent))

from src.config import settings
from src.bot.routers import tasks, common_router, profile_router, tasks_router, unknown_router

logging.basicConfig(level=logging.INFO)


async def main() -> None:
    bot = Bot(token=settings.BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    tasks.set_bot(bot)

    dp.include_router(common_router)
    dp.include_router(profile_router)
    dp.include_router(tasks_router)
    dp.include_router(unknown_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
