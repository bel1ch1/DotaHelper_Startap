from ultralytics import YOLO
import cv2

# Путь к модели
model_path = 'C:/Mirea_Projects/DotaHelper_Startap/Capturing_Dota/ml_model/best_1.pt'

# Загрузка модели
model = YOLO(model_path)

# Путь к изображению
image_path = 'C:/Mirea_Projects/DotaHelper_Startap/Capturing_Dota/ml_model/combined_screenshot_1739879532.png'

# Загрузка изображения
image = cv2.imread(image_path)

# Приведение изображения к размеру 640x640
resized_image = cv2.resize(image, (600, 440))

# Выполнение предсказания
results = model(resized_image)

# Порог уверенности
confidence_threshold = 0.3

# Список для хранения распознанных классов
detected_classes = []

# Обработка результатов
for result in results:
    boxes = result.boxes  # Bounding boxes
    for box in boxes:
        class_id = int(box.cls)  # Класс
        confidence = float(box.conf)  # Уверенность
        if confidence >= confidence_threshold:
            class_name = model.names[class_id]  # Название класса
            detected_classes.append((class_name, confidence))

# Вывод списка распознанных классов
if detected_classes:
    print("Распознанные классы:")
    for class_name, confidence in detected_classes:
        print(f"Class: {class_name}, Confidence: {confidence:.2f}")
else:
    print("Ничего не распознано.")
