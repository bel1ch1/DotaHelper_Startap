import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from tqdm import tqdm

class DotaItemsDataset(Dataset):
    def __init__(self, csv_path='/content/match_dataset.csv'):
        self.data = pd.read_csv(csv_path)
        self.target_cols = [f'target_item_{i}' for i in range(9)]
        feature_cols = [col for col in self.data.columns if col not in self.target_cols]

        self.features = self.data[feature_cols].values.astype(np.float32)
        self.features = (self.features - self.features.mean(axis=0)) / (self.features.std(axis=0) + 1e-8)

        self.targets = self.data[self.target_cols].values.astype(np.int64)
        unique_items = np.unique(self.targets)
        unique_items = unique_items[unique_items != 0]

        self.num_items = len(unique_items)
        self.item_to_class = {item: idx+1 for idx, item in enumerate(unique_items)}
        self.class_to_item = {idx+1: item for idx, item in enumerate(unique_items)}
        self.class_to_item[0] = 0

        for i in range(self.targets.shape[1]):
            for j in range(self.targets.shape[0]):
                if self.targets[j, i] != 0:
                    self.targets[j, i] = self.item_to_class[self.targets[j, i]]

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return {
            'features': torch.tensor(self.features[idx]),
            'targets': torch.tensor(self.targets[idx])
        }

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
            nn.Linear(128, num_classes * 9)
        )
        self.num_classes = num_classes

    def forward(self, x):
        batch_size = x.size(0)
        out = self.fc(x)
        return out.view(batch_size, 9, self.num_classes)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Используемое устройство: {device}")


def load_model(model_path, dataset):
    model = DotaItemsModel(
        input_size=dataset.features.shape[1],
        num_classes=dataset.num_items + 1
    ).to(device)

    # Загружаем с обработкой несоответствия размеров
    pretrained = torch.load(model_path, map_location=device)
    model.load_state_dict(pretrained, strict=False)
    model.eval()
    return model

# Загрузка модели и данных
model_path = '/content/dota_items_model.pth'
csv_path = '/content/match_dataset.csv'
dataset = DotaItemsDataset(csv_path)
model = load_model(model_path, dataset)

# Инференс на 5 примерах
test_loader = DataLoader(dataset, batch_size=1, shuffle=True)
for i, batch in enumerate(test_loader):
    if i >= 5:
        break

    features = batch['features'].to(device)
    targets = batch['targets'].cpu().numpy()[0]

    with torch.no_grad():
        outputs = model(features)
        predicted = torch.argmax(outputs, dim=2).cpu().numpy()[0]

        predicted_items = [dataset.class_to_item[p] for p in predicted]
        true_items = [dataset.class_to_item.get(t, 0) for t in targets]

        print(f"\nПример #{i+1}:")
        print("Предсказанные предметы:", predicted_items)
        print("Реальные предметы:    ", true_items)
        print("Совпадения:          ", [p==t for p,t in zip(predicted_items, true_items)])

        plt.figure(figsize=(10, 4))
        plt.bar(range(9), predicted_items, width=0.4, label='Предсказано')
        plt.bar(np.arange(9)+0.4, true_items, width=0.4, label='Реально')
        plt.xticks(range(9), [f'Слот {i}' for i in range(9)])
        plt.ylabel('ID предмета')
        plt.legend()
        plt.show()
