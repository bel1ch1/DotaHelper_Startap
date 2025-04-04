import json
import mss
import mss.tools
import time
import cv2
from PIL import Image
import pygetwindow as gw
import os
from ultralytics import YOLO

# Путь к модели YOLO
model_path = 'C:/Mirea_Projects/DotaHelper_Startap/Data_Recognition/src/ml_model/best_2.pt'

# Загрузка модели
model = YOLO(model_path)

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
            save_path = f'C:/Mirea_Projects/DotaHelper_Startap/Getting_Data_From_Dota/{filename}'
            combined_image.save(save_path)
            print(f"Скриншот сохранен: {filename}")

            # Обработка моделью
            process(save_path)

            # Удаление скрина (опционально)
            os.remove(save_path)

    else:
        print("Окно Dota 2 не активно или не найдено.")


def process(image_path):
    """
    Обработка изображения с помощью модели.
    """
    # Загрузка изображения
    image = cv2.imread(image_path)

    # Сжатие
    resized_image = cv2.resize(image, (600, 440))

    # Обработка моделью
    results = model(resized_image)

    # Порог уверенности
    confidence_threshold = 0.7

    # Список для хранения распознанных классов
    detected_classes = []

    # Флаг для проверки наличия героя
    hero_detected = False

    # Обработка результатов
    for result in results:
        boxes = result.boxes
        for box in boxes:
            class_id = int(box.cls)  # Класс
            confidence = float(box.conf)  # Уверенность
            if confidence >= confidence_threshold:
                class_name = model.names[class_id]  # Название класса
                detected_classes.append((class_name, confidence))
                if "hero" in class_name.lower():
                    hero_detected = True

    if hero_detected:
        json_data = {
            "items": []
        }
        for class_name, confidence in detected_classes:
            json_data["items"].append({
                "class": class_name,
                "confidence": confidence
            })

        # Путь к JSON файлу
        json_save_path = 'C:/Mirea_Projects/DotaHelper_Startap/Getting_Data_From_Dota/src/results.json'

        # Загрузка существующих данных, если файл существует
        if os.path.exists(json_save_path):
            with open(json_save_path, 'r') as json_file:
                existing_data = json.load(json_file)
        else:
            existing_data = {"items": []}

        # Добавление новых данных
        existing_data["items"].extend(json_data["items"])

        # Сохранение обновленного JSON
        with open(json_save_path, 'w') as json_file:
            json.dump(existing_data, json_file, indent=4)
        print(f"JSON обновлен: {json_save_path}")

    # Вывод списка распознанных классов
    if detected_classes:
        print("Распознанные классы:")
        for class_name, confidence in detected_classes:
            print(f"Class: {class_name}, Confidence: {confidence:.2f}")
    else:
        print("Ничего не распознано.")


# Точка входа
if __name__ == "__main__":
    while True:
        capture_dota2_window()
        time.sleep(0.5)
