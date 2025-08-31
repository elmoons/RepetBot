import re

from aiogram import Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from sqlalchemy import insert, select, delete

from src.database.database import async_session_maker
from src.database.models import Student
from src.parse_tasks import get_problem_info
from src.utils import check_registration


# Регулярные выражения для валидации
NAME_PATTERN = re.compile(r'^[а-яёa-z\- ]{2,}$', re.IGNORECASE)
EMAIL_PATTERN = re.compile(r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$', re.IGNORECASE)
PHONE_PATTERN = re.compile(r'^(\+7|7|8)?[\s\-]?\(?[0-9]{3}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$')


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


@dp.message(Command(commands="generate_task"))
@check_registration
async def command_test_handler(message: Message):
    problem_text = get_problem_info('math', '27245')
    await message.answer(problem_text)


@dp.message(Command(commands="registration"))
async def command_registration_handler(message: Message, state: FSMContext):
    await state.clear()

    await state.set_state(RegisterStudentState.get_student_name)
    await message.answer(
        "Привет, давай знакомиться! Напиши ФИО (Например: Иванов Иван Иванович)."
    )


@dp.message(RegisterStudentState.get_student_name)
async def get_email_student(message: Message, state: FSMContext):
    # Валидация ФИО
    name_parts = message.text.split()

    if len(name_parts) < 3:
        await message.answer("❌ Пожалуйста, введите полное ФИО через пробел (Фамилия Имя Отчество)")
        return

    for part in name_parts:
        if not NAME_PATTERN.fullmatch(part):
            await message.answer("❌ ФИО может содержать только буквы, дефисы и пробелы")
            return

    await state.update_data(student_name=message.text)
    await message.answer("Напиши мне свою электронную почту!")
    await state.set_state(RegisterStudentState.get_student_email)


@dp.message(RegisterStudentState.get_student_email)
async def get_phone_student(message: Message, state: FSMContext):
    # Валидация email
    if not EMAIL_PATTERN.fullmatch(message.text):
        await message.answer("❌ Пожалуйста, введите корректный email адрес")
        return

    await state.update_data(student_email=message.text)
    await message.answer("Напиши мне свой номер телефона (в формате +7 XXX XXX XX XX)")
    await state.set_state(RegisterStudentState.get_student_phone_number)


@dp.message(RegisterStudentState.get_student_phone_number)
async def final_of_registration(message: Message, state: FSMContext):
    # Валидация и нормализация номера телефона
    phone = message.text.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")

    if not PHONE_PATTERN.fullmatch(phone):
        await message.answer("❌ Пожалуйста, введите корректный номер телефона")
        return

    # Нормализация номера к формату +7XXXXXXXXXX
    if phone.startswith("8"):
        phone = "+7" + phone[1:]
    elif phone.startswith("7"):
        phone = "+" + phone
    elif not phone.startswith("+"):
        phone = "+7" + phone

    # Проверка длины номера
    if len(phone) != 12:
        await message.answer("❌ Номер телефона должен содержать 11 цифр")
        return

    await state.update_data(student_phone=phone)
    user_data = await state.get_data()

    # Разделение ФИО на компоненты
    name_parts = user_data['student_name'].split()
    last_name = name_parts[0]
    first_name = name_parts[1]
    patronymic = " ".join(name_parts[2:]) if len(name_parts) > 2 else ""

    try:
        async with async_session_maker() as session:
            stmt_student_add = insert(Student).values(
                tg_id=message.from_user.id,
                last_name=last_name,
                first_name=first_name,
                patronymic=patronymic,
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
    except Exception as e:
        await message.answer("❌ Произошла ошибка при сохранении данных. Попробуйте позже.")
        # Логирование ошибки
        print(f"Database error: {e}")
    finally:
        await state.clear()


@dp.message(Command(commands="get_me"))
@check_registration
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


@dp.message(Command(commands="change_my_data"))
@check_registration
async def command_change_my_data_handler(message: Message, state: FSMContext):
    await state.clear()
    async with async_session_maker() as session:
        query = delete(Student).where(Student.tg_id == message.from_user.id)
        await session.execute(query)
        await session.commit()
    await state.set_state(RegisterStudentState.get_student_name)
    await message.answer(
        "Напиши ФИО (Например: Иванов Иван Иванович)."
    )


@dp.message()
@check_registration
async def handle_unknown_message(message: Message):
    await message.answer(
        "Я не понимаю это сообщение. Пожалуйста, используй команды из меню."
    )
