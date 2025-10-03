import base64
import io
import re

import cairosvg
from aiogram import Dispatcher, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    Message,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    BufferedInputFile,
)
from sqlalchemy import insert, select, delete

from src.config import settings
from src.convert_images import image_to_base64
from src.database.database import async_session_maker
from src.database.models import Student
from src.parse_tasks import get_problem_info, get_random_task_id
from src.utils import check_registration

# Регулярные выражения для валидации
NAME_PATTERN = re.compile(r"^[а-яёa-z\- ]{2,}$", re.IGNORECASE)
EMAIL_PATTERN = re.compile(r"^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$", re.IGNORECASE)
PHONE_PATTERN = re.compile(
    r"^(\+7|7|8)?[\s\-]?\(?[0-9]{3}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$"
)


dp = Dispatcher(storage=MemoryStorage())
bot = Bot(token=settings.BOT_TOKEN)


class RegisterStudentState(StatesGroup):
    get_student_name = State()
    get_student_email = State()
    get_student_phone_number = State()


class TaskStates(StatesGroup):
    waiting_for_solution = State()


@dp.message(CommandStart())
async def command_start_handler(message: Message):
    await message.answer(
        f"Привет! Этот бот содержит задания ОГЭ/ЕГЭ по Математике!\n"
        f"Список команд находится в меню!"
    )


@dp.message(Command(commands="get_info"))
async def command_get_info_handler(message: Message):
    await message.answer("""
    **💡Этот бот поможет тебе готовиться к экзаменам пр математике формата ОГЭ и ЕГЭ. 
🕖Он сэкономит твое время, ведь тебе нет необходимости в поиске подходящих заданий для подготовки. 
👊Он является твоим тренером; с его помощью ты сможешь расширить свои способности и кругозор разнообразия заданий экзамена.**
""")


math_task_numbers = [
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "10",
    "11",
    "12",
    "13",
    "14",
    "15",
    "16",
    "17",
    "18",
    "19",
]


@dp.message(Command(commands="generate_task"))
@check_registration
async def command_test_handler(message: Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=str(i)) for i in math_task_numbers[:5]],
            [KeyboardButton(text=str(i)) for i in math_task_numbers[5:10]],
            [KeyboardButton(text=str(i)) for i in math_task_numbers[10:15]],
            [KeyboardButton(text=str(i)) for i in math_task_numbers[15:19]],
            [KeyboardButton(text="Отмена")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    await message.answer(
        "📚 Выберите номер задания ЕГЭ по математике:", reply_markup=keyboard
    )


@dp.message(F.text.in_(math_task_numbers))
async def handle_task_selection(message: Message, state: FSMContext):
    task_number = message.text

    await state.update_data(task_number=task_number)

    task_id = get_random_task_id(int(task_number))
    problem_info = get_problem_info("math", f"{task_id}")

    solution_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Получить решение")],
            [KeyboardButton(text="🔁 Выбрать другое задание")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    await message.answer(
        f"📝 Задание №{task_number} ({problem_info["id_of_task"]}):\n\n{problem_info['condition_clean']}",
        reply_markup=solution_keyboard,
    )

    image_tasks = problem_info["images_task"]
    print(image_tasks)
    for i in range(len(image_tasks)):
        svg_coded_string = image_to_base64(image_tasks[i])
        try:
            # Декодируем base64 SVG
            svg_bytes = base64.b64decode(svg_coded_string)

            # Конвертируем SVG в PNG
            png_bytes = io.BytesIO()
            cairosvg.svg2png(bytestring=svg_bytes, write_to=png_bytes)
            png_bytes.seek(0)

            # Отправляем PNG как фото
            await bot.send_photo(
                chat_id=message.from_user.id,
                photo=BufferedInputFile(png_bytes.getvalue(), filename="image.png"),
            )
        except Exception as e:
            await message.reply(f"Произошла ошибка при отправке изображения: {e}")

    await state.set_state(TaskStates.waiting_for_solution)
    await state.update_data(problem_info=problem_info)


@dp.message(F.text == "✅ Получить решение", TaskStates.waiting_for_solution)
async def handle_solution_request(message: Message, state: FSMContext):
    data = await state.get_data()
    task_number = data.get("task_number")
    problem_info = data.get("problem_info")

    await message.answer(
        f"✅ Решение для задания №{task_number} ({problem_info["id_of_task"]}):\n\n{problem_info['solution_clean']}",
        reply_markup=ReplyKeyboardRemove(),
    )
    solution_tasks = problem_info["images_solution"]

    print(solution_tasks)
    for i in range(len(solution_tasks)):
        svg_coded_string = image_to_base64(solution_tasks[i])
        try:
            # Декодируем base64 SVG
            svg_bytes = base64.b64decode(svg_coded_string)

            # Конвертируем SVG в PNG
            png_bytes = io.BytesIO()
            cairosvg.svg2png(bytestring=svg_bytes, write_to=png_bytes)
            png_bytes.seek(0)

            # Отправляем PNG как фото
            await bot.send_photo(
                chat_id=message.from_user.id,
                photo=BufferedInputFile(png_bytes.getvalue(), filename="image.png"),
            )
        except Exception as e:
            await message.reply(f"Произошла ошибка при отправке изображения: {e}")

    await state.clear()
    await state.update_data(problem_info=problem_info)


@dp.message(F.text == "🔁 Выбрать другое задание", TaskStates.waiting_for_solution)
async def handle_change_task(message: Message, state: FSMContext):
    await state.clear()

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=str(i)) for i in math_task_numbers[:5]],
            [KeyboardButton(text=str(i)) for i in math_task_numbers[5:10]],
            [KeyboardButton(text=str(i)) for i in math_task_numbers[10:15]],
            [KeyboardButton(text=str(i)) for i in math_task_numbers[15:19]],
            [KeyboardButton(text="Отмена")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    await message.answer(
        "📚 Выберите номер задания ЕГЭ по математике:", reply_markup=keyboard
    )


@dp.message(F.text == "Отмена")
async def handle_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Выбор задания отменен", reply_markup=ReplyKeyboardRemove())


@dp.message(Command(commands="registration"))
async def command_registration_handler(message: Message, state: FSMContext):
    await state.clear()

    async with async_session_maker() as session:
        query = select(Student).filter_by(tg_id=message.from_user.id)
        result = await session.execute(query)
        student_data = result.scalars().one_or_none()
        if student_data:
            await state.clear()
            await message.answer(
                "Вы уже зарегистрированы, если хотите изменить свои данные, используйте /change_my_data"
            )
            return

    await state.set_state(RegisterStudentState.get_student_name)
    await message.answer(
        "Привет, давай знакомиться! Напиши ФИО (Например: Иванов Иван Иванович)."
    )


@dp.message(RegisterStudentState.get_student_name)
async def get_email_student(message: Message, state: FSMContext):
    # Валидация ФИО
    name_parts = message.text.split()

    if len(name_parts) < 3:
        await message.answer(
            "❌ Пожалуйста, введите полное ФИО через пробел (Фамилия Имя Отчество)"
        )
        return

    for part in name_parts:
        if not NAME_PATTERN.fullmatch(part):
            await message.answer(
                "❌ ФИО может содержать только буквы, дефисы и пробелы"
            )
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
    await message.answer("Напиши мне свой номер телефона")
    await state.set_state(RegisterStudentState.get_student_phone_number)


@dp.message(RegisterStudentState.get_student_phone_number)
async def final_of_registration(message: Message, state: FSMContext):
    # Валидация и нормализация номера телефона
    phone = (
        message.text.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    )

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
    name_parts = user_data["student_name"].split()
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
                email=user_data["student_email"],
                number_phone=user_data["student_phone"],
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
        await message.answer(
            "❌ Произошла ошибка при сохранении данных. Попробуйте позже."
        )
    finally:
        await state.clear()


@dp.message(Command(commands="get_me"))
@check_registration
async def command_registration_handler(message: Message):
    async with async_session_maker() as session:
        query = select(Student).filter_by(tg_id=message.from_user.id)
        result = await session.execute(query)
        student_data = result.scalars().one_or_none()
    if not (student_data):
        return
    await message.answer(
        f"Ваши данные:\n"
        f"👤 ФИО: {student_data.last_name + ' ' + student_data.first_name + ' ' + student_data.patronymic}\n"
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
    await message.answer("Необходимо заново пройти регистрацию по команде /register")


@dp.message()
@check_registration
async def handle_unknown_message(message: Message):
    await message.answer(
        "Я не понимаю это сообщение. Пожалуйста, используй команды из меню."
    )
