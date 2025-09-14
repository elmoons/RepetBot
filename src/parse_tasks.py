import random

from mako.testing.helpers import result_lines
from sdamgia import SdamGIA

def clean_sdamgia_text(text: str) -> str:
    cleaned = text.replace('­', '').replace('\xad', '')
    cleaned = cleaned.replace('\u202f', ' ').replace('\u2009', ' ')
    return ' '.join(cleaned.split())


def get_problem_info(subject: str, problem_id: str):
    sdamgia = SdamGIA()

    result = sdamgia.get_problem_by_id(subject, problem_id)
    # print(result)
    condition_clean = clean_sdamgia_text(result['condition']['text'])
    solution_clean = clean_sdamgia_text(result['solution']['text'])
    images_task = result['condition']['images']
    images_solution = result['solution']['images']
    # print(result)
    # Задача: {result['id']}
    # Тема: {result['topic']}
    # Ответ: {result['answer']}
    # Решение: {solution_clean}
    data_task = {
        "condition_clean": condition_clean,
        "images_task": images_task,
        "solution_clean": solution_clean,
        "images_solution": images_solution
        }

    return data_task

# print(get_problem_info('math', '27245'))


def get_random_category_by_number(number_of_task: int):
    """
    Находит нужный номер задачи и возвращает случайную категорию из него
    Возвращает: (category_id) или None если не найдено
    """
    sdamgia = SdamGIA()
    catalog = sdamgia.get_catalog('math')
    # print(catalog)
    target_topic = None
    for topic in catalog:
        if topic['topic_id'] == str(number_of_task):
            target_topic = topic
            break

    random_category = random.choice(target_topic['categories'])
    category_id = random_category['category_id']

    return category_id


def get_random_task_id(number_of_task: int):
    sdamgia = SdamGIA()
    is_not_emptiness = True
    while (is_not_emptiness):
        result = sdamgia.get_category_by_id("math", get_random_category_by_number(number_of_task), random.randint(1,5))
        if (result):
            is_not_emptiness = False
    random_task_id = result[random.randint(0, len(result) - 1)]
    return random_task_id
