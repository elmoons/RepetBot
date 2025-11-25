start_message = (
    "Привет! Этот бот содержит задания ОГЭ/ЕГЭ по Математике!\n "
    "Список команд находится в меню!"
)

get_info_message = (
    "💡Этот бот поможет тебе готовиться к экзаменам пр математике формата ОГЭ и ЕГЭ.\n"
    "🕖Он сэкономит твое время, ведь тебе нет необходимости в поиске подходящих заданий для подготовки.\n"
    "👊Он является твоим тренером; с его помощью ты сможешь расширить свои способности и кругозор разнообразия заданий экзамена."
)

select_task_number_ege_math_prof_message = (
    "📚 Выберите номер задания ЕГЭ Математика Профильная:"
)

select_task_number_ege_math_base_message = (
    "📚 Выберите номер задания ЕГЭ Математика Базовая:"
)

select_task_number_oge_math_base_message = "📚 Выберите номер задания ОГЭ Математика:"

cancel_task_message = "Выбор задания отменен"

send_image_error_message = "Произошла ошибка при отправке изображения"


def generate_task_condition_message(task_number, id_of_task, condition_clean):
    return f"📝 Задание №{task_number} ({id_of_task}):\n\n{condition_clean}"


def generate_task_solution_message(task_number, id_of_task, solution_clean):
    return f"✅ Решение для задания №{task_number} ({id_of_task}):\n\n{solution_clean}"


get_user_name_message = (
    "Привет, давай знакомиться! Напиши ФИО (Например: Иванов Иван Иванович)."
)

user_full_name_error_message = (
    "❌ Пожалуйста, введите полное ФИО через пробел (Фамилия Имя Отчество)"
)

user_name_symbols_error_message = (
    "❌ ФИО может содержать только буквы, дефисы и пробелы"
)

get_user_phone_message = "Напишите мне свой номер телефона"

user_phone_correct_error_message = "❌ Пожалуйста, введите корректный номер телефона"

user_phone_len_error_message = "❌ Номер телефона должен содержать 11 цифр"

get_user_email_message = "Напишите мне свою электронную почту!"

user_email_error_message = "❌ Пожалуйста, введите корректный email адрес"

select_exam_message = "Выбери тип экзамена:"

select_exam_error_message = "❌ Пожалуйста, выбери экзамен с клавиатуры"

registration_error = "❌ Произошла ошибка при сохранении данных. Попробуйте позже."

no_registration_message = (
    "❌ Перед использованием необходимо зарегистрироваться\n"
    "👉 Используй команду /registration"
)

already_register_message = "Вы уже зарегистрированы, если хотите изменить свои данные или вид экзамена, используйте /change_my_data . Вам будет предложено заново пройти регистрацию."

change_my_data_message = "Необходимо заново пройти регистрацию по команде /registration"

unknown_message = "Я не понимаю это сообщение. Пожалуйста, используй команды из меню."


def generate_registration_completed_message(
    last_name, first_name, patronymic, email, number_phone, type_of_exam
):
    return f"""✅ Регистрация завершена!\n👤 ФИО: {last_name + " " + first_name + " " + patronymic}\n📧 Email: {email}\n📞 Телефон: {number_phone}\n📑 Экзамен: {type_of_exam}\n▶️ Теперь можешь пользоваться всеми функциями!"""


def generate_get_me_message(
    last_name, first_name, patronymic, email, number_phone, type_of_exam
):
    return f"""Ваши данные:\n👤 ФИО: {last_name + " " + first_name + " " + patronymic}\n📧 Email: {email}\n📞 Телефон: {number_phone}\n📑 Экзамен: {type_of_exam}"""
