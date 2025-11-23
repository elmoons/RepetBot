import re
from functools import wraps
from aiogram.types import Message
from sqlalchemy import select

from src.database.database import async_session_maker
from src.database.models import Student

# Регулярные выражения для валидации
NAME_PATTERN = re.compile(r"^[а-яёa-z\- ]{2,}$", re.IGNORECASE)
EMAIL_PATTERN = re.compile(r"^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$", re.IGNORECASE)
PHONE_PATTERN = re.compile(
    r"^(\+7|7|8)?[\s\-]?\(?[0-9]{3}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$"
)

VALID_EXAMS = [
    "ЕГЭ Математика Профильная",
    "ЕГЭ Математика Базовая",
    "ОГЭ Математика",
]


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
