from functools import wraps
from aiogram.types import Message
from sqlalchemy import select

from src.database.database import async_session_maker
from src.database.models import Student


def check_registration(handler):
    @wraps(handler)
    async def wrapper(message: Message, *args, **kwargs):
        async with async_session_maker() as session:
            query = select(Student).where(Student.tg_id == message.from_user.id)
            result = await session.execute(query)
            student = result.scalar_one_or_none()

        if student:
            return await handler(message, *args, **kwargs)
        else:
            await message.answer(
                "❌ Перед использованием необходимо зарегистрироваться\n"
                "👉 Используй команду /registration"
            )

    return wrapper

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
    "20",
    "21",
    "22",
    "23",
    "24",
    "25",
]