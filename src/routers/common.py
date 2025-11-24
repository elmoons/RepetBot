from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from src.messages import start_message, get_info_message, unknown_message
from src.utils import check_registration

common_router = Router()


@common_router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(start_message, reply_markup=ReplyKeyboardRemove())


@common_router.message(Command(commands="get_info"))
async def command_get_info_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(get_info_message, reply_markup=ReplyKeyboardRemove())


@common_router.message()
@check_registration
async def handle_unknown_message(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(unknown_message, reply_markup=ReplyKeyboardRemove())
