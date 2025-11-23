import base64

from aiogram import Dispatcher, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    Message,
    ReplyKeyboardRemove,
    BufferedInputFile,
)
from sqlalchemy import insert, select, delete

from src.config import settings
from src.convert_images import image_to_base64, svg_to_telegram_png
from src.database.database import async_session_maker
from src.database.models import Student
from src.keyboards import (
    math_task_numbers,
    keyboard_math_oge,
    keyboard_math_base,
    keyboard_math_prof,
    exam_selection_keyboard,
    solution_keyboard,
    new_task_keyboard,
)
from src.messages import (
    unknown_message,
    change_my_data_message,
    generate_get_me_message,
    start_message,
    get_info_message,
    select_task_number_ege_math_prof_message,
    select_task_number_ege_math_base_message,
    select_task_number_oge_math_base_message,
    registration_error,
    generate_registration_completed_message,
    select_exam_error_message,
    select_exam_message,
    get_user_name_message,
    already_register_message,
    cancel_task_message,
    get_user_phone_message,
    send_image_error_message,
)
from src.parse_tasks import get_problem_info, get_random_task_id
from src.utils import (
    check_registration,
    NAME_PATTERN,
    EMAIL_PATTERN,
    PHONE_PATTERN,
    VALID_EXAMS,
)

dp = Dispatcher(storage=MemoryStorage())
bot = Bot(token=settings.BOT_TOKEN)


class RegisterStudentState(StatesGroup):
    get_student_name = State()
    get_student_email = State()
    get_student_phone_number = State()
    get_student_target_exam = State()


class TaskStates(StatesGroup):
    waiting_for_solution = State()


@dp.message(CommandStart())
async def command_start_handler(message: Message):
    await message.answer(start_message, reply_markup=ReplyKeyboardRemove())


@dp.message(Command(commands="get_info"))
async def command_get_info_handler(message: Message):
    await message.answer(get_info_message, reply_markup=ReplyKeyboardRemove())


@dp.message(Command(commands="generate_task"))
@check_registration
async def command_test_handler(message: Message, state: FSMContext):
    await state.clear()

    async with async_session_maker() as session:
        query = select(Student).filter_by(tg_id=message.from_user.id)
        result = await session.execute(query)
        student_data = result.scalars().one_or_none()
        exam = student_data.type_of_exam

    if exam == "ЕГЭ Математика Профильная":
        await message.answer(
            select_task_number_ege_math_prof_message,
            reply_markup=keyboard_math_prof,
        )
    elif exam == "ЕГЭ Математика Базовая":
        await message.answer(
            select_task_number_ege_math_base_message,
            reply_markup=keyboard_math_base,
        )
    elif exam == "ОГЭ Математика":
        await message.answer(
            select_task_number_oge_math_base_message, reply_markup=keyboard_math_oge
        )


@dp.message(F.text.in_(math_task_numbers))
@check_registration
async def handle_task_selection(message: Message, state: FSMContext):
    task_number = message.text
    await state.update_data(task_number=task_number)

    async with async_session_maker() as session:
        query = select(Student).filter_by(tg_id=message.from_user.id)
        result = await session.execute(query)
        student_data = result.scalars().one_or_none()
        exam = student_data.type_of_exam

    # if exam == "ЕГЭ Математика Профильная":
    #
    # elif exam == "ЕГЭ Математика Базовая":
    #
    # elif exam == "ОГЭ Математика":

    task_id = get_random_task_id(int(task_number))
    problem_info = get_problem_info("math", f"{task_id}")

    await message.answer(
        f"📝 Задание №{task_number} ({problem_info['id_of_task']}):\n\n{problem_info['condition_clean']}",
        reply_markup=solution_keyboard,
    )

    image_tasks = problem_info["images_task"]
    for i in range(len(image_tasks)):
        svg_coded_string = image_to_base64(image_tasks[i])
        try:
            svg_bytes = base64.b64decode(svg_coded_string)
            final_png = svg_to_telegram_png(svg_bytes, target_size=(400, 300))

            await bot.send_photo(
                chat_id=message.from_user.id,
                photo=BufferedInputFile(final_png.getvalue(), filename="image.png"),
            )

        except Exception:
            await message.reply(send_image_error_message)

    await state.set_state(TaskStates.waiting_for_solution)
    await state.update_data(problem_info=problem_info)


@dp.message(F.text == "✅ Получить решение", TaskStates.waiting_for_solution)
@check_registration
async def handle_solution_request(message: Message, state: FSMContext):
    data = await state.get_data()
    task_number = data.get("task_number")
    problem_info = data.get("problem_info")

    await message.answer(
        f"✅ Решение для задания №{task_number} ({problem_info['id_of_task']}):\n\n{problem_info['solution_clean']}",
        reply_markup=new_task_keyboard,
    )
    solution_tasks = problem_info["images_solution"]

    for i in range(len(solution_tasks)):
        svg_coded_string = image_to_base64(solution_tasks[i])
        try:
            svg_bytes = base64.b64decode(svg_coded_string)
            final_png = svg_to_telegram_png(svg_bytes, target_size=(400, 300))

            await bot.send_photo(
                chat_id=message.from_user.id,
                photo=BufferedInputFile(final_png.getvalue(), filename="image.png"),
                reply_markup=new_task_keyboard,
            )
        except Exception:
            await message.reply(send_image_error_message)

    await state.clear()


@dp.message(F.text == "▶️ Следующее задание")
@check_registration
async def handle_new_task_request(message: Message):
    await command_test_handler(message)


@dp.message(F.text == "🔁 Выбрать другое задание", TaskStates.waiting_for_solution)
@check_registration
async def handle_change_task(message: Message, state: FSMContext):
    await state.clear()

    async with async_session_maker() as session:
        query = select(Student).filter_by(tg_id=message.from_user.id)
        result = await session.execute(query)
        student_data = result.scalars().one_or_none()
        exam = student_data.type_of_exam

    if exam == "ЕГЭ Математика Профильная":
        await message.answer(
            select_task_number_ege_math_prof_message,
            reply_markup=keyboard_math_prof,
        )
    elif exam == "ЕГЭ Математика Базовая":
        await message.answer(
            select_task_number_ege_math_base_message,
            reply_markup=keyboard_math_base,
        )
    elif exam == "ОГЭ Математика":
        await message.answer(
            select_task_number_oge_math_base_message, reply_markup=keyboard_math_oge
        )


@dp.message(F.text == "Отмена")
@check_registration
async def handle_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(cancel_task_message, reply_markup=ReplyKeyboardRemove())


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
                already_register_message, reply_markup=ReplyKeyboardRemove()
            )
            return

    await state.set_state(RegisterStudentState.get_student_name)
    await message.answer(get_user_name_message, reply_markup=ReplyKeyboardRemove())


@dp.message(RegisterStudentState.get_student_name)
async def get_email_student(message: Message, state: FSMContext):
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
    await message.answer("Напишите мне свою электронную почту!")
    await state.set_state(RegisterStudentState.get_student_email)


@dp.message(RegisterStudentState.get_student_email)
async def get_phone_student(message: Message, state: FSMContext):
    # Валидация email
    if not EMAIL_PATTERN.fullmatch(message.text):
        await message.answer("❌ Пожалуйста, введите корректный email адрес")
        return

    await state.update_data(student_email=message.text)
    await message.answer(get_user_phone_message)
    await state.set_state(RegisterStudentState.get_student_phone_number)


@dp.message(RegisterStudentState.get_student_phone_number)
async def get_phone_student(message: Message, state: FSMContext):
    phone = (
        message.text.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    )

    if not PHONE_PATTERN.fullmatch(phone):
        await message.answer("❌ Пожалуйста, введите корректный номер телефона")
        return

    if phone.startswith("8"):
        phone = "+7" + phone[1:]
    elif phone.startswith("7"):
        phone = "+" + phone
    elif not phone.startswith("+"):
        phone = "+7" + phone

    if len(phone) != 12:
        await message.answer("❌ Номер телефона должен содержать 11 цифр")
        return

    await state.update_data(student_phone=phone)

    await message.answer(select_exam_message, reply_markup=exam_selection_keyboard)
    await state.set_state(RegisterStudentState.get_student_target_exam)


@dp.message(RegisterStudentState.get_student_target_exam)
async def get_target_exam_student(message: Message, state: FSMContext):
    exam_type = message.text.strip()

    if exam_type not in VALID_EXAMS:
        await message.answer(select_exam_error_message)
        return
    await state.update_data(student_exam=exam_type)
    user_data = await state.get_data()

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
                type_of_exam=user_data["student_exam"],
            )
            await session.execute(stmt_student_add)
            await session.commit()

        await message.answer(
            generate_registration_completed_message(),
            reply_markup=ReplyKeyboardRemove(),
        )
    except Exception:
        await message.answer(registration_error, reply_markup=ReplyKeyboardRemove())
    finally:
        await state.clear()


@dp.message(Command(commands="get_me"))
@check_registration
async def command_registration_handler(message: Message, state: FSMContext):
    await state.clear()
    async with async_session_maker() as session:
        query = select(Student).filter_by(tg_id=message.from_user.id)
        result = await session.execute(query)
        student_data = result.scalars().one()
    await message.answer(
        generate_get_me_message(
            student_data.last_name,
            student_data.first_name,
            student_data.patronymic,
            student_data.email,
            student_data.number_phone,
            student_data.type_of_exam,
        ),
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.message(Command(commands="change_my_data"))
@check_registration
async def command_change_my_data_handler(message: Message, state: FSMContext):
    await state.clear()
    async with async_session_maker() as session:
        query = delete(Student).where(Student.tg_id == message.from_user.id)
        await session.execute(query)
        await session.commit()
    await message.answer(change_my_data_message, reply_markup=ReplyKeyboardRemove())


@dp.message()
@check_registration
async def handle_unknown_message(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(unknown_message, reply_markup=ReplyKeyboardRemove())
