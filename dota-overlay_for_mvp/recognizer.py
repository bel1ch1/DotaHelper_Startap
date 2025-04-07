import cv2
import json
import numpy as np
import onnxruntime as ort
from ultralytics import YOLO

# Конфигурация
MODEL_PATH = '/home/bell/wkorkStaff/DotaHelper_Startap/dota-overlay_for_mvp/best.pt'
IMAGE_PATH = '/home/bell/wkorkStaff/DotaHelper_Startap/dota-overlay_for_mvp/test_recognizer.py/combined_screenshot_1743890805.png'
CONFIDENCE_THRESHOLD = 0.8

# Словарь соответствия названий/ID предметов и их позиций в векторе
ITEM_MAPPING = {
    # Константные поля (0-20)
    "stage": 0,
    "kill_advantage": 1,
    "team_advantage": 2,
    "enemy_hero_0": 3,
    "enemy_hero_1": 4,
    "enemy_hero_2": 5,
    "enemy_hero_3": 6,
    "enemy_hero_4": 7,
    "ally_hero_0": 8,
    "ally_hero_1": 9,
    "ally_hero_2": 10,
    "ally_hero_3": 11,
    "enemy_wr_0": 12,
    "enemy_wr_1": 13,
    "enemy_wr_2": 14,
    "enemy_wr_3": 15,
    "enemy_wr_4": 16,
    "ally_wr_0": 17,
    "ally_wr_1": 18,
    "ally_wr_2": 19,
    "ally_wr_3": 20,
    
    # Поля предметов (21-49)
    "Ghost Scepter": 21,
    "Dust of Appearance": 22,
    "Scythe of Vyse": 23,
    "Orchid Malevolence": 24,
    "Euls Scepter of Divinity": 25,
    "Force Staff": 26,
    "Dagon": 27,
    "Pipe of Insight": 28,
    "Urn of Shadows": 29,
    "Medallion of Courage": 30,
    "Shadow Blade": 31,
    "Glimmer Cape": 32,
    "Solar Crest": 33,
    "Aether Lens": 34,
    "Spirit Vessel": 35,
    "Holy Locket": 36,
    "Nullifier": 37,
    "Lotus Orb": 38,
    "Meteor Hammer": 39,
    "Null Talisman": 40,
    "Wraith Band": 41,
    "Bracer": 42,
    "Aghanims Shard": 43,
    "Wind Waker": 44,
    "Diffusal Blade": 45,
    "Ethereal Blade": 46,
    "Overwhelming Blink": 47,
    "Swift Blink": 48,
    "Arcane Blink": 49
}

class DotaPredictor:
    def __init__(self, onnx_path, metadata_path):
        # Загрузка модели ONNX
        self.session = ort.InferenceSession(onnx_path)

        # Загрузка метаданных
        with open(metadata_path) as f:
            self.meta = json.load(f)

        self.feature_means = np.array(self.meta['feature_means'])
        self.feature_stds = np.array(self.meta['feature_stds'])
        self.class_to_item = {int(k): int(v) for k, v in self.meta['class_to_item'].items()}

    def preprocess(self, features):
        """Нормализация входных данных"""
        features = np.array(features, dtype=np.float32)
        return (features - self.feature_means) / (self.feature_stds + 1e-8)

    def predict(self, features):
        """Выполнение предсказания"""
        inputs = self.preprocess(features)

        # ONNX ожидает float32 и правильную shape
        inputs = inputs.astype(np.float32).reshape(1, -1)

        outputs = self.session.run(
            None, {'input': inputs}
        )[0]  # Получаем первый выход

        # Преобразуем выходы в предметы
        pred_classes = np.argmax(outputs, axis=2).squeeze()
        return [self.class_to_item[c] for c in pred_classes]



def create_initial_vector():
    """Создает начальный вектор с константными значениями (50 элементов)"""
    return [
        # Константные поля (0-20)
        2,                      # stage (0)
        1.0,                    # kill_advantage (1)
        -0.04202477398865634,   # team_advantage (2)
        63,                     # enemy_hero_0 (3)
        88,                     # enemy_hero_1 (4)
        29,                     # enemy_hero_2 (5)
        6,                      # enemy_hero_3 (6)
        74,                     # enemy_hero_4 (7)
        97,                     # ally_hero_0 (8)
        18,                     # ally_hero_1 (9)
        27,                     # ally_hero_2 (10)
        64,                     # ally_hero_3 (11)
        0.54,                   # enemy_wr_0 (12)
        0.563,                  # enemy_wr_1 (13)
        0.489,                  # enemy_wr_2 (14)
        0.513,                  # enemy_wr_3 (15)
        0.581,                  # enemy_wr_4 (16)
        0.535,                  # ally_wr_0 (17)
        0.522,                  # ally_wr_1 (18)
        0.586,                  # ally_wr_2 (19)
        0.551,                  # ally_wr_3 (20)
        
        # Поля для предметов (21-49)
        *[0] * 29
    ]


def process_image(image_path, model):
    """Обрабатывает изображение и возвращает вектор из 50 значений"""
    data_vector = create_initial_vector()
    detected_items = []
    
    try:
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError("Не удалось загрузить изображение")
            
        resized_image = cv2.resize(image, (600, 440))
        results = model(resized_image)
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                if float(box.conf) >= CONFIDENCE_THRESHOLD:
                    class_id = int(box.cls)
                    class_name = model.names[class_id]
                    
                    # Проверяем соответствие предмета
                    if class_name in ITEM_MAPPING:
                        pos = ITEM_MAPPING[class_name]
                        if 21 <= pos <= 49:  # Проверяем, что это поле предмета
                            data_vector[pos] = 1
                            detected_items.append((class_name, pos))
        
        return data_vector, detected_items
    
    except Exception as e:
        print(f"Ошибка обработки изображения: {e}")
        return data_vector, []

def print_vector_info(vector, detected_items):
    """Выводит подробную информацию о векторе"""
    print("\n" + "="*60)
    print("ФИНАЛЬНЫЙ ВЕКТОР ДАННЫХ (50 ЭЛЕМЕНТОВ)")
    print("="*60)
    
    # Вывод структуры вектора
    print("\nСтруктура вектора:")
    for name, pos in sorted(ITEM_MAPPING.items(), key=lambda x: x[1]):
        value = vector[pos]
        print(f"[{pos:2d}] {name:20s}: {value}")
    
    # Вывод обнаруженных предметов
    if detected_items:
        print("\nОбнаруженные предметы:")
        for item_name, pos in detected_items:
            print(f"- {item_name} (позиция {pos})")
    
    # Вывод полного вектора
    print("\nВектор в формате списка:")
    print(vector)

if __name__ == "__main__":
    mapa = {
    20:"Circlet",
    96: "Scythe of Vyse",
    116: "Black King Bar",
    147: "Manta Style",
    0: "Blink dagger", 
    11: "Quelling Blade",
    39: "Healing Salve",
    603: "Swift Blink"
    }
    # Инициализация модели
    yolo_model = YOLO(MODEL_PATH)
    
    # Обработка изображения
    result_vector, detected_items = process_image(IMAGE_PATH, yolo_model)
        # Инициализация
    print(result_vector)
    predictor = DotaPredictor(
        onnx_path="model.onnx",
        metadata_path="model_metadata.json"
    )

    # Предсказание
    items = predictor.predict(result_vector)
    for item in items:
        print(mapa.get(item))

