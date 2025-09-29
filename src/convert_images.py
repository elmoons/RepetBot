import requests
import base64


def image_to_base64(url: str) -> str:
    try:
        # Скачиваем изображение
        response = requests.get(url)
        response.raise_for_status()

        # Кодируем в base64
        image_bytes = response.content
        base64_string = base64.b64encode(image_bytes).decode("utf-8")

        return base64_string

    except Exception as e:
        print(f"Ошибка: {e}")
        return None


# print(image_to_base64("https://math-ege.sdamgia.ru/get_file?id=20487"))
# print(image_to_base64("https://ege.sdamgia.ru/formula/svg/71/71be21f76a77293c9ecbc4ab250b4c16.svg"))
