from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from src.bot import unknown_message, check_registration

unknown_router = Router()


@unknown_router.message()
@check_registration
async def handle_unknown_message(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(unknown_message, reply_markup=ReplyKeyboardRemove())
