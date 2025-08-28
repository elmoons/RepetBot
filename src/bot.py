from aiogram import Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from sqlalchemy import insert, select

from src.database.database import async_session_maker
from src.database.models import Student
from src.parse_tasks import get_problem_info

dp = Dispatcher(storage=MemoryStorage())

class RegisterStudentState(StatesGroup):
    get_student_name = State()
    get_student_email = State()
    get_student_phone_number = State()


@dp.message(CommandStart())
async def command_start_handler(message: Message):
    await message.answer(
        f"Привет! Этот бот содержит задания ОГЭ/ЕГЭ по Математике!\n"
        f"Список команд находится в меню!"
    )


@dp.message(Command(commands="get_info"))
async def command_get_info_handler(message: Message):
    await message.answer("Этот бот поможет тебе в подготовке к ЕГЭ/ОГЭ")


@dp.message(Command(commands="get_problem"))
async def command_test_handler(message: Message):
    problem_text = get_problem_info('math', '27245')
    await message.answer(problem_text)


@dp.message(Command(commands="registration"))
async def command_registration_handler(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(RegisterStudentState.get_student_name)
    await message.answer(
        "Привет, давай знакомиться! Напиши ФИО."
    )


@dp.message(RegisterStudentState.get_student_name)
async def get_email_student(message: Message, state: FSMContext):
    await state.update_data(student_name=message.text)
    await message.answer("Напиши мне свою электронную почту!")
    await state.set_state(RegisterStudentState.get_student_email)


@dp.message(RegisterStudentState.get_student_email)
async def get_phone_student(message: Message, state: FSMContext):
    await state.update_data(student_email=message.text)
    await message.answer("Напиши мне свой номер телефона")
    await state.set_state(RegisterStudentState.get_student_phone_number)


@dp.message(RegisterStudentState.get_student_phone_number)
async def final_of_registration(message: Message, state: FSMContext):
    await state.update_data(student_phone=message.text)
    user_data = await state.get_data()

    async with async_session_maker() as session:
        stmt_student_add = insert(Student).values(
            tg_id=message.from_user.id,
            last_name=user_data['student_name'].split(' ')[0],
            first_name=user_data['student_name'].split(' ')[1],
            patronymic=user_data['student_name'].split(' ')[2],
            email=user_data['student_email'],
            number_phone=user_data['student_phone'],
        )
        await session.execute(stmt_student_add)
        await session.commit()

    await message.answer(
        f"✅ Регистрация завершена!\n"
        f"👤 ФИО: {user_data['student_name']}\n"
        f"📧 Email: {user_data['student_email']}\n"
        f"📞 Телефон: {user_data['student_phone']}\n"
        f"Теперь можешь пользоваться всеми функциями!"
    )
    await state.clear()

@dp.message(Command(commands="get_me"))
async def command_registration_handler(message: Message):
    async with async_session_maker() as session:
        query = select(Student)
        result = await session.execute(query)
        student_data = result.scalars().one()

    await message.answer(
        f"Ваши данные:\n"
        f"👤 ФИО: {student_data.first_name + " " + student_data.last_name}\n"
        f"📧 Email: {student_data.email}\n"
        f"📞 Телефон: {student_data.number_phone}\n"
    )
