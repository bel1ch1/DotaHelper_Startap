import json
import numpy as np
import onnxruntime as ort

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

# Пример использования
if __name__ == "__main__":
    # Инициализация
    predictor = DotaPredictor(
        onnx_path="model.onnx",
        metadata_path="model_metadata.json"
    )


    example_input = [2,1.0,-0.04202477398865634,63,88,29,6,74,97,18,27,64,0.54,0.563,0.489,0.513,0.581,0.535,0.522,0.586,0.551,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0
]

    # Предсказание
    items = predictor.predict(example_input)
    print("Предсказанные предметы:", items)
