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
            # Пропорции для обрезки
            left_crop_ratio = 0.25  # 10% от ширины окна
            right_crop_ratio = 0.25  # 10% от ширины окна
            top_region_height_ratio = 0.1  # 10% от высоты окна
            bottom_region_height_ratio = 0.2  # 20% от высоты окна

            # Рассчитываем размеры областей захвата
            left_crop = int(width * left_crop_ratio)
            right_crop = int(width * right_crop_ratio)
            top_region_height = int(height * top_region_height_ratio)
            bottom_region_height = int(height * bottom_region_height_ratio)

            # Верхняя часть
            top_region = {
                'top': top,
                'left': left + left_crop,
                'width': width - left_crop - right_crop,
                'height': top_region_height
            }
            top_screenshot = sct.grab(top_region)

            # Нижняя часть
            bottom_region = {
                'top': top + height - bottom_region_height,
                'left': left + left_crop,
                'width': width - left_crop - right_crop,
                'height': bottom_region_height
            }
            bottom_screenshot = sct.grab(bottom_region)

            # Преобразуем снимки в изображения PIL и переводим в оттенки серого
            top_image = Image.frombytes('RGB', top_screenshot.size, top_screenshot.rgb).convert('L')
            bottom_image = Image.frombytes('RGB', bottom_screenshot.size, bottom_screenshot.rgb).convert('L')

            # Склеивание 2-ух скринов
            combined_image = Image.new('L', (top_image.width, top_image.height + bottom_image.height))
            combined_image.paste(top_image, (0, 0))
            combined_image.paste(bottom_image, (0, top_image.height))

            # Сохранение
            filename = f'combined_screenshot_{int(time.time())}.png'
            save_path = f'C:/work/DotaHelper_Startap/Capturing_Dota/src/Captured_screens/{filename}'
            combined_image.save(save_path)
            print(f"Скриншот сохранен: {filename}")

    else:
        print("Окно Dota 2 не активно или не найдено.")

# Точка входа
if __name__ == "__main__":
    for i in range(1000):
        capture_dota2_window()
        time.sleep(3)  # Задержка
