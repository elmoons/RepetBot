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

get_user_name_message = "Привет, давай знакомиться! Напиши ФИО (Например: Иванов Иван Иванович)."

already_register_message = "Вы уже зарегистрированы, если хотите изменить свои данные или вид экзамена, используйте /change_my_data"

select_exam_message = "Выбери тип экзамена:"

select_exam_error_message = "❌ Пожалуйста, выбери экзамен с клавиатуры"

registration_error = "❌ Произошла ошибка при сохранении данных. Попробуйте позже."

change_my_data_message = "Необходимо заново пройти регистрацию по команде /registration"

unknown_message = "Я не понимаю это сообщение. Пожалуйста, используй команды из меню."


def generate_registration_completed_message(
    last_name, first_name, patronymic, email, number_phone, type_of_exam
):
    return (
        f"""✅ Регистрация завершена!\n
        👤 ФИО: {last_name + " " + first_name + " " + patronymic}\n
        📧 Email: {email}\n
        📞 Телефон: {number_phone}\n
        📑 Экзамен: {type_of_exam}\n
        ▶️ Теперь можешь пользоваться всеми функциями!""",
    )


def generate_get_me_message(
    last_name, first_name, patronymic, email, number_phone, type_of_exam
):
    return f"""Ваши данные:\n
        👤 ФИО: {last_name + " " + first_name + " " + patronymic}\n
        📧 Email: {email}\n
        📞 Телефон: {number_phone}\n
        📑 Экзамен: {type_of_exam}"""
