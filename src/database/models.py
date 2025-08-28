from sqlalchemy.orm import Mapped, mapped_column
from src.database.database import BaseOrm


class Student(BaseOrm):
    __tablename__ = "students_data"
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(unique=True)
    first_name: Mapped[str] = mapped_column()
    last_name: Mapped[str] = mapped_column()
    patronymic: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column(unique=True)
    number_phone: Mapped[str] = mapped_column(unique=True)
