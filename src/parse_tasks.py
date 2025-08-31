import random
from sdamgia import SdamGIA


def clean_sdamgia_text(text: str) -> str:
    cleaned = text.replace('­', '').replace('\xad', '')
    cleaned = cleaned.replace('\u202f', ' ').replace('\u2009', ' ')
    return ' '.join(cleaned.split())


def get_problem_info(subject: str, problem_id: str):
    sdamgia = SdamGIA()

    result = sdamgia.get_problem_by_id(subject, problem_id)
    print(result)
    condition_clean = clean_sdamgia_text(result['condition']['text'])
    solution_clean = clean_sdamgia_text(result['solution']['text'])
    images_task = result['condition']['images']
    images_solution = result['solution']['images']
    # print(result)
    # Задача: {result['id']}
    # Тема: {result['topic']}
    # Ответ: {result['answer']}
    # Решение: {solution_clean}

    return f"{result['id']} {condition_clean} {images_task} {images_solution} {solution_clean}"



# Использование
# print(get_problem_info('math', '27245'))


def get_random_category_by_number(number_of_task: int):
    """
    Находит нужный номер задачи и возвращает случайную категорию из него
    Возвращает: (category_id) или None если не найдено
    """
    sdamgia = SdamGIA()
    catalog = sdamgia.get_catalog('math')
    print(catalog)
    target_topic = None
    for topic in catalog:
        if topic['topic_id'] == str(number_of_task):
            target_topic = topic
            break

    random_category = random.choice(target_topic['categories'])
    category_id = random_category['category_id']

    return category_id

print(get_random_category_by_number(1))

def get_random_task(number_of_task: int):
    sdamgia = SdamGIA()
    result = sdamgia.get_category_by_id("math", '79')
    print(result)

get_random_task(1)