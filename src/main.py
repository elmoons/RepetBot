import asyncio
import logging
import sys
from pathlib import Path

from aiogram import Bot

sys.path.append(str(Path(__file__).parent.parent))

from src.bot import dp
from src.config import settings


logging.basicConfig(level=logging.INFO)


async def main() -> None:
    bot = Bot(token=settings.BOT_TOKEN,)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
