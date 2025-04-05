from ultralytics import YOLO
import cv2
import json
import os

# Модель
model_path = 'C:/work/DotaHelper_Startap/Data_Recognition/src/ml_model/best_2.pt'
model = YOLO(model_path)

# Обработка изображения
image_path = 'C:/work/DotaHelper_Startap/Data_Recognition/src/ml_model/combined_screenshot_1740163193.png'
image = cv2.imread(image_path)
if image is None:
    raise FileNotFoundError(f"Не удалось загрузить изображение по пути: {image_path}")
resized_image = cv2.resize(image, (600, 440))

# Порог уверенности
confidence_threshold = 0.8

# Списки классов (замените на реальные из вашей модели)
all_heroes = ['Shadow Fiend arcana - hero', 'hero2', 'hero3']  # Все возможные герои
enemy_heroes = ['Shadow Fiend arcana - hero', 'hero3']        # Только вражеские герои

# Файл для сохранения предметов
items_file = 'enemy_items.json'

# Загрузка существующих предметов
enemy_items = []
if os.path.exists(items_file):
    try:
        with open(items_file, 'r') as f:
            enemy_items = json.load(f)
            if not isinstance(enemy_items, list):
                enemy_items = []
    except (json.JSONDecodeError, IOError):
        enemy_items = []

# Обработка результатов
save_items = False
current_items = []
detected_objects = {}

results = model(resized_image)

for result in results:
    boxes = result.boxes
    for box in boxes:
        confidence = float(box.conf)
        if confidence < confidence_threshold:
            continue

        class_id = int(box.cls)
        class_name = model.names[class_id]
        detected_objects[class_name] = confidence

        # Проверка на вражеского героя
        if class_name in enemy_heroes:
            save_items = True

        # Добавление в предметы (если не герой)
        if class_name not in all_heroes:
            current_items.append(class_name)

# Вывод результатов
print("\nРезультаты обнаружения:")
for obj, conf in detected_objects.items():
    print(f"- {obj} (уверенность: {conf:.2f})")

# Сохранение предметов (если есть вражеские герои)
if save_items:
    new_items = [item for item in current_items if item not in enemy_items]
    if new_items:
        enemy_items.extend(new_items)
        with open(items_file, 'w') as f:
            json.dump(enemy_items, f, indent=4)
        print(f"\nДобавлено {len(new_items)} новых предметов:")
        for item in new_items:
            print(f"- {item}")
        print(f"\nОбщее количество предметов: {len(enemy_items)}")
    else:
        print("\nНовых предметов не обнаружено.")
elif not detected_objects:
    print("\nНичего не обнаружено на изображении.")
else:
    print("\nВражеские герои не обнаружены - предметы не сохраняются.")

print(f"\nТекущий список предметов сохранен в {items_file}")
