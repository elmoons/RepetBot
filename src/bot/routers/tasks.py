import base64

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    Message,
    ReplyKeyboardRemove,
    BufferedInputFile,
)
from sqlalchemy import select

from src.parser import (
    image_to_base64,
    svg_to_telegram_png,
    get_problem_info,
    get_random_task_id,
)
from src.database import async_session_maker, Student
from src.bot import (
    math_task_numbers,
    math_oge_keyboard,
    math_base_keyboard,
    math_prof_keyboard,
    solution_keyboard,
    new_task_keyboard,
    check_registration,
    select_task_number_ege_math_prof_message,
    select_task_number_ege_math_base_message,
    select_task_number_oge_math_base_message,
    cancel_task_message,
    send_image_error_message,
    generate_task_condition_message,
    generate_task_solution_message,
)

tasks_router = Router()
bot_instance = None


def set_bot(bot: Bot):
    global bot_instance
    bot_instance = bot


class TaskStates(StatesGroup):
    waiting_for_solution = State()


@tasks_router.message(Command(commands="generate_task"))
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
            reply_markup=math_prof_keyboard,
        )
    elif exam == "ЕГЭ Математика Базовая":
        await message.answer(
            select_task_number_ege_math_base_message,
            reply_markup=math_base_keyboard,
        )
    elif exam == "ОГЭ Математика":
        await message.answer(
            select_task_number_oge_math_base_message, reply_markup=math_oge_keyboard
        )


@tasks_router.message(F.text.in_(math_task_numbers))
@check_registration
async def handle_task_selection(message: Message, state: FSMContext):
    task_number = message.text
    await state.update_data(task_number=task_number)

    async with async_session_maker() as session:
        query = select(Student).filter_by(tg_id=message.from_user.id)
        result = await session.execute(query)
        student_data = result.scalars().one_or_none()
        exam = student_data.type_of_exam

    subject = ""
    if exam == "ЕГЭ Математика Профильная":
        exam = "ege"
        subject = "math"
    elif exam == "ЕГЭ Математика Базовая":
        exam = "ege"
        subject = "mathb"
    elif exam == "ОГЭ Математика":
        exam = "oge"
        subject = "math"

    task_id = get_random_task_id(exam, subject, int(task_number))
    problem_info = get_problem_info(exam, subject, f"{task_id}")

    await message.answer(
        generate_task_condition_message(
            task_number, problem_info["id_of_task"], problem_info["condition_clean"]
        ),
        reply_markup=solution_keyboard,
    )

    image_tasks = problem_info["images_task"]
    for i in range(len(image_tasks)):
        svg_coded_string = image_to_base64(image_tasks[i])
        try:
            svg_bytes = base64.b64decode(svg_coded_string)
            final_png = svg_to_telegram_png(svg_bytes, target_size=(400, 300))

            await bot_instance.send_photo(
                chat_id=message.from_user.id,
                photo=BufferedInputFile(final_png.getvalue(), filename="image.png"),
            )

        except Exception:
            await message.reply(send_image_error_message)

    await state.set_state(TaskStates.waiting_for_solution)
    await state.update_data(problem_info=problem_info)


@tasks_router.message(F.text == "✅ Получить решение", TaskStates.waiting_for_solution)
@check_registration
async def handle_solution_request(message: Message, state: FSMContext):
    data = await state.get_data()
    task_number = data.get("task_number")
    problem_info = data.get("problem_info")

    await message.answer(
        generate_task_solution_message(
            task_number, problem_info["id_of_task"], problem_info["solution_clean"]
        ),
        reply_markup=new_task_keyboard,
    )
    solution_tasks = problem_info["images_solution"]

    for i in range(len(solution_tasks)):
        svg_coded_string = image_to_base64(solution_tasks[i])
        try:
            svg_bytes = base64.b64decode(svg_coded_string)
            final_png = svg_to_telegram_png(svg_bytes, target_size=(400, 300))

            await bot_instance.send_photo(
                chat_id=message.from_user.id,
                photo=BufferedInputFile(final_png.getvalue(), filename="image.png"),
                reply_markup=new_task_keyboard,
            )
        except Exception:
            await message.reply(send_image_error_message)

    await state.clear()


@tasks_router.message(F.text == "▶️ Следующее задание")
@check_registration
async def handle_new_task_request(message: Message, state: FSMContext):
    await command_test_handler(message, state)


@tasks_router.message(
    F.text == "🔁 Выбрать другое задание", TaskStates.waiting_for_solution
)
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
            reply_markup=math_prof_keyboard,
        )
    elif exam == "ЕГЭ Математика Базовая":
        await message.answer(
            select_task_number_ege_math_base_message,
            reply_markup=math_base_keyboard,
        )
    elif exam == "ОГЭ Математика":
        await message.answer(
            select_task_number_oge_math_base_message, reply_markup=math_oge_keyboard
        )


@tasks_router.message(F.text == "Отмена")
@check_registration
async def handle_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(cancel_task_message, reply_markup=ReplyKeyboardRemove())
