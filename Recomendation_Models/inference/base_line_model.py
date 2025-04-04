import torch
import numpy as np
from torch import nn

class DotaItemsModel(nn.Module):
    def __init__(self, input_size, num_classes):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(input_size, 256),
            nn.ReLU(),
            nn.BatchNorm1d(256),
            nn.Dropout(0.3),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.BatchNorm1d(128),
            nn.Dropout(0.3),
            nn.Linear(128, num_classes * 9)  # 9 слотов предметов
        )
        self.num_classes = num_classes

    def forward(self, x):
        return self.fc(x).view(x.size(0), 9, self.num_classes)


class DotaPredictor:
    def __init__(self, model_path):
        checkpoint = torch.load(model_path, map_location='cpu')

        self.model = DotaItemsModel(
            input_size=checkpoint['input_size'],
            num_classes=len(checkpoint['class_to_item'])
        )
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model.eval()

        self.class_to_item = checkpoint['class_to_item']
        self.feature_means = checkpoint['feature_means']
        self.feature_stds = checkpoint['feature_stds']

    def preprocess(self, features):
        """Нормализация входных признаков"""
        features = np.array(features, dtype=np.float32)
        return (features - self.feature_means) / (self.feature_stds + 1e-8)

    def predict(self, input_features):
        """Предсказание предметов"""
        with torch.no_grad():
            inputs = torch.tensor(
                self.preprocess(input_features),
                dtype=torch.float32
            ).unsqueeze(0)

            outputs = self.model(inputs)
            preds = torch.argmax(outputs, dim=2).squeeze().numpy()
            return [self.class_to_item[p] for p in preds]
