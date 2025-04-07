import json
import cv2
from PIL import Image

import os
from ultralytics import YOLO

# Путь к модели YOLO
model_path = '/home/bell/wkorkStaff/DotaHelper_Startap/dota-overlay_for_mvp/best.pt'

# Загрузка модели
model = YOLO(model_path)

            

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
    confidence_threshold = 0.8

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
        json_save_path = '/home/bell/wkorkStaff/DotaHelper_Startap/dota-overlay_for_mvp/results.json'

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
    save_path = '/home/bell/wkorkStaff/DotaHelper_Startap/dota-overlay_for_mvp/test_recognizer.py/combined_screenshot_1743890805.png'
    # Обработка моделью
    process(save_path)