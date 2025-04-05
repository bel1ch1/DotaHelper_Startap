from ultralytics import YOLO
import cv2

# Модель
model_path = 'C:/work/DotaHelper_Startap/Data_Recognition/src/ml_model/best_2.pt'
model = YOLO(model_path)

# Обработка изображения
image_path = 'C:/work/DotaHelper_Startap/Data_Recognition/src/ml_model/combined_screenshot_1740163193.png'
image = cv2.imread(image_path)
resized_image = cv2.resize(image, (600, 440))

results = model(resized_image)

confidence_threshold = 0.8  # Порог уверенности
object_counter = 1          # Счетчик объектов
detected_objects = {}

# Обработка результатов
for result in results:
    boxes = result.boxes  # Bounding boxes
    for box in boxes:
        class_id = int(box.cls)  # Класс
        confidence = float(box.conf)  # Уверенность
        if confidence >= confidence_threshold:
            class_name = model.names[class_id]  # Название класса
            # Сохраняем сопоставление: номер -> (класс, уверенность)
            detected_objects[object_counter] = (class_name, confidence)
            object_counter += 1

if detected_objects:
    for number, (class_name, confidence) in detected_objects.items():
        print(f"{number}: {class_name}, Confidence: {confidence:.2f}")
else:
    print("Ничего не распознано.")
