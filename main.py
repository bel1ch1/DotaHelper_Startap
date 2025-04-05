import mss.tools
import time
from PIL import Image
import pygetwindow as gw
from ultralytics import YOLO
import json
import os

# Constantes
MODEL_PATH = 'C:/work/DotaHelper_Startap/Data_Recognition/src/ml_model/best_2.pt'
SCREENSHOTS_DIR = 'C:/work/DotaHelper_Startap/Capturing_Dota/src/Captured_screens'
RESULTS_DIR = 'C:/work/DotaHelper_Startap/Capturing_Dota/src/Results'
CONFIDENCE_THRESHOLD = 0.8  # Порог уверенности для детекции
CAPTURE_DELAY = 3  # Задержка между скриншотами (секунды)

os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# Model
model = YOLO(MODEL_PATH)

def capture_and_process():
    """Захватывает скриншот, обрабатывает его и удаляет после распознавания."""
    dota_windows = gw.getWindowsWithTitle('Dota 2')

    if not dota_windows or not dota_windows[0].isActive:
        print("Окно Dota 2 не активно или не найдено.")
        return None

    window = dota_windows[0]
    left, top, width, height = window.left, window.top, window.width, window.height

    with mss.mss() as sct:
        # Области захвата (верхняя и нижняя части)
        left_crop = int(width * 0.25)
        right_crop = int(width * 0.25)
        top_height = int(height * 0.1)
        bottom_height = int(height * 0.2)

        # Делаем скриншоты
        top_shot = sct.grab({
            'top': top,
            'left': left + left_crop,
            'width': width - left_crop - right_crop,
            'height': top_height
        })
        bottom_shot = sct.grab({
            'top': top + height - bottom_height,
            'left': left + left_crop,
            'width': width - left_crop - right_crop,
            'height': bottom_height
        })

        # Склеиваем изображение
        combined = Image.new('RGB', (top_shot.width, top_shot.height + bottom_shot.height))
        combined.paste(Image.frombytes('RGB', top_shot.size, top_shot.rgb), (0, 0))
        combined.paste(Image.frombytes('RGB', bottom_shot.size, bottom_shot.rgb), (0, top_shot.height))

        # Сохраняем скриншот временно
        timestamp = int(time.time())
        screenshot_path = f'{SCREENSHOTS_DIR}/combined_{timestamp}.png'
        combined.save(screenshot_path)

        # Обработка моделью YOLO
        results = model(combined.resize((600, 440)))  # Масштабируем для модели
        detected_objects = {}

        for result in results:
            for box in result.boxes:
                if float(box.conf) >= CONFIDENCE_THRESHOLD:
                    class_name = model.names[int(box.cls)]
                    detected_objects[len(detected_objects) + 1] = {
                        'class': class_name,
                        'confidence': float(box.conf),
                        'timestamp': timestamp
                    }

        # Сохраняем результаты в JSON
        if detected_objects:
            result_path = f'{RESULTS_DIR}/result_{timestamp}.json'
            with open(result_path, 'w') as f:
                json.dump(detected_objects, f, indent=4)
            print(f"Обнаружено объектов: {len(detected_objects)}. Результаты сохранены в {result_path}")
        else:
            print("Ничего не распознано.")

        # Удаляем скриншот после обработки
        os.remove(screenshot_path)
        print(f"Скриншот {screenshot_path} удалён.")

        return detected_objects

# Основной цикл
if __name__ == "__main__":
    try:
        while True:
            capture_and_process()
            time.sleep(CAPTURE_DELAY)
    except KeyboardInterrupt:
        print("Программа остановлена пользователем.")
