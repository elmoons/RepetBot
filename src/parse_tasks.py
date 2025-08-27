from sdamgia import SdamGIA


def clean_sdamgia_text(text: str) -> str:
    cleaned = text.replace('­', '').replace('\xad', '')
    cleaned = cleaned.replace('\u202f', ' ').replace('\u2009', ' ')
    return ' '.join(cleaned.split())


def get_problem_info(subject: str, problem_id: str):
    sdamgia = SdamGIA()

    result = sdamgia.get_problem_by_id(subject, problem_id)

    condition_clean = clean_sdamgia_text(result['condition']['text'])
    solution_clean = clean_sdamgia_text(result['solution']['text'])

    # print(f"Задача #{result['id']}")
    # print(f"Тема: {result['topic']}")
    return f"{condition_clean}"
    # print(f"Ответ: {result['answer']}")
    # print(f"Решение:\n{solution_clean}")


# Использование
print(get_problem_info('math', '27245'))