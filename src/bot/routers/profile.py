from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import (
    Message,
    ReplyKeyboardRemove,
)
from sqlalchemy import insert, select, delete

from src.database import async_session_maker, Student

from src.bot import (
    change_my_data_message,
    generate_get_me_message,
    registration_error,
    generate_registration_completed_message,
    select_exam_error_message,
    select_exam_message,
    get_user_name_message,
    already_register_message,
    get_user_phone_message,
    get_user_email_message,
    user_email_error_message,
    user_full_name_error_message,
    user_phone_len_error_message,
    user_phone_correct_error_message,
    user_name_symbols_error_message,
    exam_selection_keyboard,
    check_registration,
    NAME_PATTERN,
    EMAIL_PATTERN,
    PHONE_PATTERN,
    VALID_EXAMS,
)

profile_router = Router()


class RegisterStudentState(StatesGroup):
    get_student_name = State()
    get_student_email = State()
    get_student_phone_number = State()
    get_student_target_exam = State()


@profile_router.message(Command(commands="registration"))
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


@profile_router.message(RegisterStudentState.get_student_name)
async def get_email_student(message: Message, state: FSMContext):
    name_parts = message.text.split()

    if len(name_parts) < 3:
        await message.answer(user_full_name_error_message)
        return

    for part in name_parts:
        if not NAME_PATTERN.fullmatch(part):
            await message.answer(user_name_symbols_error_message)
            return

    await state.update_data(student_name=message.text)
    await message.answer(get_user_email_message)
    await state.set_state(RegisterStudentState.get_student_email)


@profile_router.message(RegisterStudentState.get_student_email)
async def get_phone_student(message: Message, state: FSMContext):
    if not EMAIL_PATTERN.fullmatch(message.text):
        await message.answer(user_email_error_message)
        return

    await state.update_data(student_email=message.text)
    await message.answer(get_user_phone_message)
    await state.set_state(RegisterStudentState.get_student_phone_number)


@profile_router.message(RegisterStudentState.get_student_phone_number)
async def get_phone_student(message: Message, state: FSMContext):
    phone = (
        message.text.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    )

    if not PHONE_PATTERN.fullmatch(phone):
        await message.answer(user_phone_correct_error_message)
        return

    if phone.startswith("8"):
        phone = "+7" + phone[1:]
    elif phone.startswith("7"):
        phone = "+" + phone
    elif not phone.startswith("+"):
        phone = "+7" + phone

    if len(phone) != 12:
        await message.answer(user_phone_len_error_message)
        return

    await state.update_data(student_phone=phone)

    await message.answer(select_exam_message, reply_markup=exam_selection_keyboard)
    await state.set_state(RegisterStudentState.get_student_target_exam)


@profile_router.message(RegisterStudentState.get_student_target_exam)
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
            generate_registration_completed_message(
                last_name,
                first_name,
                patronymic,
                user_data["student_email"],
                user_data["student_phone"],
                user_data["student_exam"],
            ),
            reply_markup=ReplyKeyboardRemove(),
        )
    except Exception:
        await message.answer(registration_error, reply_markup=ReplyKeyboardRemove())
    finally:
        await state.clear()


@profile_router.message(Command(commands="get_me"))
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


@profile_router.message(Command(commands="change_my_data"))
@check_registration
async def command_change_my_data_handler(message: Message, state: FSMContext):
    await state.clear()
    async with async_session_maker() as session:
        query = delete(Student).where(Student.tg_id == message.from_user.id)
        await session.execute(query)
        await session.commit()
    await message.answer(change_my_data_message, reply_markup=ReplyKeyboardRemove())
