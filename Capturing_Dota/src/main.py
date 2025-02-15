"""  Программа для захвата частей экрана доты  """

import mss
import mss.tools
import time
from PIL import Image
import pygetwindow as gw
import os

def capture_dota2_window():
    # Находим окно Dota 2
    dota_windows = gw.getWindowsWithTitle('Dota 2')

    # Проверяем, активно ли окно Dota 2
    if dota_windows and dota_windows[0].isActive:
        dota_window = dota_windows[0]

        # Получаем координаты окна Dota 2
        left, top, width, height = dota_window.left, dota_window.top, dota_window.width, dota_window.height

        with mss.mss() as sct:
            top_region = {
                'top': top,
                'left': left,
                'width': width,
                'height': 100  # Высота верхней части
            }
            top_screenshot = sct.grab(top_region)

            bottom_region = {
                'top': top + height - 300,  # 300 пикселей снизу (включая 100 вверх)
                'left': left,
                'width': width,
                'height': 300  # Высота нижней части
            }
            bottom_screenshot = sct.grab(bottom_region)

            # Преобразуем снимки в изображения PIL
            top_image = Image.frombytes('RGB', top_screenshot.size, top_screenshot.rgb)
            bottom_image = Image.frombytes('RGB', bottom_screenshot.size, bottom_screenshot.rgb)

            # Склеивание 2-ух скринов
            combined_image = Image.new('RGB', (top_image.width, top_image.height + 200))
            combined_image.paste(top_image, (0, 0))
            combined_image.paste(bottom_image.crop((0, 100, bottom_image.width, bottom_image.height)), (0, top_image.height))

            # Сохранение
            filename = f'combined_screenshot_{int(time.time())}.png'
            combined_image.save(filename)
            print(f"Скриншот сохранен: {filename}")

            # Обработка моделью
            process(filename)

            # Удаление скрина
            os.remove(filename)

    else:
        print("Окно Dota 2 не активно или не найдено.")


def process(filename):
    """
    Заглушка для обработки изображения с помощью модели распознавания.
    """
    print(f"Изображение {filename} передано в YOLO для обработки.")
    time.sleep(1)


# Точка входа
if __name__ == "__main__":
    for i in range(100):
        capture_dota2_window()
        time.sleep(10)
