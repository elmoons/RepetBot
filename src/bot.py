from aiogram import Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message

from src.parse_tasks import get_problem_info

dp = Dispatcher(storage=MemoryStorage())


@dp.message(CommandStart())
async def command_start_handler(message: Message):
    await message.answer(
        f"Привет! Этот бот содержит задания ОГЭ/ЕГЭ по Математике!\n"
        f"Список команд находится в меню!"
    )


@dp.message(Command(commands="command1"))
async def command_test_handler(message: Message):
    problem_text = get_problem_info('math', '27245')
    await message.answer(problem_text)
