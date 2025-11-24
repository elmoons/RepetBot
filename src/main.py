import asyncio
import logging
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

sys.path.append(str(Path(__file__).parent.parent))

from src.config import settings
from src.routers import common, profile, tasks

logging.basicConfig(level=logging.INFO)


async def main() -> None:
    bot = Bot(token=settings.BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    tasks.set_bot(bot)

    dp.include_router(profile.profile_router)
    dp.include_router(tasks.tasks_router)
    dp.include_router(common.common_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
