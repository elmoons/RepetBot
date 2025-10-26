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


from PIL import Image
import io
import cairosvg

def svg_to_telegram_png(svg_bytes, target_size=(800, 800)):
    # Конвертируем SVG в PNG
    png_bytes = io.BytesIO()
    cairosvg.svg2png(bytestring=svg_bytes, write_to=png_bytes)
    png_bytes.seek(0)

    # Загружаем в PIL
    original = Image.open(png_bytes)
    original_width, original_height = original.size

    target_width, target_height = target_size

    # Создаем новый холст
    final_image = Image.new("RGBA", target_size, (255, 255, 255, 255))

    # Вычисляем координаты, чтобы центрировать
    x = (target_width - original_width) // 2
    y = (target_height - original_height) // 2

    final_image.paste(original, (x, y), original if original.mode == "RGBA" else None)

    # Сохраняем в байты
    final_bytes = io.BytesIO()
    final_image.convert("RGB").save(final_bytes, format="PNG")
    final_bytes.seek(0)

    return final_bytes


# print(image_to_base64("https://math-ege.sdamgia.ru/get_file?id=20487"))
# print(image_to_base64("https://ege.sdamgia.ru/formula/svg/71/71be21f76a77293c9ecbc4ab250b4c16.svg"))
