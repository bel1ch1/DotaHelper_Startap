""" Программа для сбора данных  """

import mss.tools
import time
from PIL import Image
import pygetwindow as gw


def capture_dota2_window():
    # Находим окно Dota 2
    dota_windows = gw.getWindowsWithTitle('Dota 2')

    # Проверяем, активно ли окно Dota 2
    if dota_windows and dota_windows[0].isActive:
        dota_window = dota_windows[0]

        # Получаем координаты окна Dota 2
        left, top, width, height = dota_window.left, dota_window.top, dota_window.width, dota_window.height

        with mss.mss() as sct:
            # Обрезаем левую и правую части на 100 пикселей
            left_crop = 450
            right_crop = 450

            # Верхняя часть
            top_region = {
                'top': top,
                'left': left + left_crop,  # Обрезаем слева
                'width': width - left_crop - right_crop,  # Уменьшаем ширину
                'height': 100  # Высота верхней части
            }
            top_screenshot = sct.grab(top_region)

            # Нижняя часть
            bottom_region = {
                'top': top + height - 300,  # 300 пикселей снизу (включая 100 вверх)
                'left': left + left_crop,  # Обрезаем слева
                'width': width - left_crop - right_crop,  # Уменьшаем ширину
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
            save_path = f'C:/Mirea_Projects/DotaHelper_Startap/Capturing_Dota/Captured_screens/{filename}'
            combined_image.save(save_path)
            print(f"Скриншот сохранен: {filename}")

    else:
        print("Окно Dota 2 не активно или не найдено.")


# Точка входа
if __name__ == "__main__":
    for i in range(1000):
        capture_dota2_window()
        time.sleep(3) # Задержка
