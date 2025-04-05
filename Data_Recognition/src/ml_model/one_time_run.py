from ultralytics import YOLO
import cv2
import json
import re
from datetime import datetime

# Конфигурация
MODEL_PATH = 'C:/work/DotaHelper_Startap/Data_Recognition/src/ml_model/best_2.pt'
IMAGE_PATH = 'C:/work/DotaHelper_Startap/Data_Recognition/src/ml_model/combined_screenshot_1740163193.png'
OUTPUT_JSON = 'detection_results.json'
CONFIDENCE_THRESHOLD = 0.8  # Порог уверенности для фильтрации
HERO_PATTERN = re.compile(r'(.+?)hero')  # Шаблон для извлечения имени героя

def extract_hero_name(class_name):
    """Извлекает имя героя из названия класса"""
    match = HERO_PATTERN.search(class_name)
    return match.group(1) if match else None

def process_image(image_path, model):
    """Обрабатывает изображение и возвращает структурированные данные"""
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Изображение не найдено: {image_path}")

    resized_image = cv2.resize(image, (600, 440))
    results = model(resized_image)

    detection_data = {
        'hero': None,
        'items': [],
        'timestamp': datetime.now().isoformat(),
        'image_size': f"{image.shape[1]}x{image.shape[0]}"
    }

    for result in results:
        for box in result.boxes:
            if float(box.conf) < CONFIDENCE_THRESHOLD:
                continue

            class_name = model.names[int(box.cls)]
            bbox = [round(float(x), 2) for x in box.xyxy[0].tolist()]

            # Обработка героев
            print(class_name)
            if '- hero' in class_name:
                hero_name = extract_hero_name(class_name)
                if hero_name:
                    detection_data['hero'] = {
                        'name': hero_name,
                        'full_class': class_name,
                        'confidence': round(float(box.conf), 4),
                        'bbox': bbox
                    }
            # Обработка предметов
            else:
                detection_data['items'].append({
                    'class': class_name,
                    'confidence': round(float(box.conf), 4),
                    'bbox': bbox
                })

    return detection_data

def save_to_json(data, filename):
    """Сохраняет данные в JSON файл"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Результаты сохранены в {filename}")

def main():
    try:
        # Инициализация модели
        model = YOLO(MODEL_PATH)

        # Обработка изображения
        detection_data = process_image(IMAGE_PATH, model)
        res = (list(detection_data.items()))
        print(res)
        # Вывод и сохранение результатов
        if detection_data['hero']:
            print(f"Герой обнаружен: {detection_data['hero']['name']} "
                  f"(уверенность: {detection_data['hero']['confidence']:.2f})")

            if detection_data['items']:
                print("\nОбнаруженные предметы:")
                for item in detection_data['items']:
                    print(f"- {item['class']} (уверенность: {item['confidence']:.2f})")
        else:
            print("Герои не обнаружены")

        save_to_json(detection_data, OUTPUT_JSON)

    except Exception as e:
        print(f"Ошибка: {str(e)}")

if __name__ == "__main__":
    main()
