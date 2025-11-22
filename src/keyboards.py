from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

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

keyboard_math_prof = ReplyKeyboardMarkup(
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

keyboard_math_base = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=str(i)) for i in math_task_numbers[:5]],
        [KeyboardButton(text=str(i)) for i in math_task_numbers[5:10]],
        [KeyboardButton(text=str(i)) for i in math_task_numbers[10:15]],
        [KeyboardButton(text=str(i)) for i in math_task_numbers[15:21]],
        [KeyboardButton(text="Отмена")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

keyboard_math_oge = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=str(i)) for i in math_task_numbers[:5]],
        [KeyboardButton(text=str(i)) for i in math_task_numbers[5:10]],
        [KeyboardButton(text=str(i)) for i in math_task_numbers[10:15]],
        [KeyboardButton(text=str(i)) for i in math_task_numbers[15:20]],
        [KeyboardButton(text=str(i)) for i in math_task_numbers[20:25]],
        [KeyboardButton(text="Отмена")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)
