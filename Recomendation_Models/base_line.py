import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

class DotaItemsDataset(Dataset):
    def __init__(self, csv_path):
        self.data = pd.read_csv(csv_path)

        # Отделяем target_items (предметы игрока) от остальных признаков
        self.target_cols = [f'target_item_{i}' for i in range(9)]
        feature_cols = [col for col in self.data.columns if col not in self.target_cols]

        # Нормализация фичей
        self.features = self.data[feature_cols].values.astype(np.float32)
        self.features = (self.features - self.features.mean(axis=0)) / (self.features.std(axis=0) + 1e-8)

        # Обработка target_items
        self.targets = self.data[self.target_cols].values.astype(np.int64)

        # Создаем маппинг ID предметов -> классы (исключая 0)
        unique_items = np.unique(self.targets)
        unique_items = unique_items[unique_items != 0]
        self.num_items = len(unique_items)

        self.item_to_class = {int(item): idx+1 for idx, item in enumerate(unique_items)}
        self.class_to_item = {idx+1: int(item) for idx, item in enumerate(unique_items)}
        self.class_to_item[0] = 0  # Для отсутствия предмета

        # Преобразуем target items в индексы классов
        for i in range(self.targets.shape[1]):
            for j in range(self.targets.shape[0]):
                if self.targets[j, i] != 0:
                    self.targets[j, i] = self.item_to_class[int(self.targets[j, i])]

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
            nn.Linear(128, num_classes * 9)  # 9 слотов для предметов игрока
        )
        self.num_classes = num_classes

    def forward(self, x):
        batch_size = x.size(0)
        out = self.fc(x)
        return out.view(batch_size, 9, self.num_classes)  # (batch, slots, items)

def train_model():
    # Параметры
    csv_path = 'match_dataset.csv'
    batch_size = 64
    epochs = 200
    learning_rate = 0.0001

    # Загрузка данных
    dataset = DotaItemsDataset(csv_path)

    # Разделение на train/test
    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = torch.utils.data.random_split(dataset, [train_size, val_size])

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size)

    # Инициализация модели
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = DotaItemsModel(
        input_size=dataset.features.shape[1],
        num_classes=dataset.num_items + 1  # +1 для нулевого класса
    ).to(device)

    criterion = nn.CrossEntropyLoss(ignore_index=0)
    optimizer = optim.Adam(model.parameters(), lr=learning_rate, weight_decay=1e-5)

    # Обучение
    print("Начинаем обучение модели предсказания предметов игрока...")
    for epoch in range(epochs):
        model.train()
        train_loss = 0.0

        for batch in train_loader:
            features = batch['features'].to(device)
            targets = batch['targets'].to(device)

            optimizer.zero_grad()
            outputs = model(features)

            # Loss для каждого слота предметов
            loss = 0
            for i in range(9):
                loss += criterion(outputs[:, i, :], targets[:, i])

            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

            train_loss += loss.item()

        # Валидация
        model.eval()
        val_loss = 0.0
        correct = 0
        total = 0

        with torch.no_grad():
            for batch in val_loader:
                features = batch['features'].to(device)
                targets = batch['targets'].cpu().numpy()

                outputs = model(features)
                predicted = torch.argmax(outputs, dim=2).cpu().numpy()

                # Вычисляем loss
                for i in range(9):
                    val_loss += criterion(outputs[:, i, :],
                                        torch.tensor(targets[:, i]).to(device)).item()

                # Точность (только для непустых слотов)
                mask = targets != 0
                correct += (predicted[mask] == targets[mask]).sum()
                total += mask.sum()

        val_accuracy = 100 * correct / total if total > 0 else 0
        print(f"Epoch {epoch+1}/{epochs}")
        print(f"Train Loss: {train_loss/len(train_loader):.4f}")
        print(f"Val Loss: {val_loss/len(val_loader):.4f}")
        print(f"Val Accuracy: {val_accuracy:.2f}%")
        print("-" * 50)

    # Тестирование и примеры предсказаний
    test_model(model, dataset, device)

def test_model(model, dataset, device):
    model.eval()
    sample = next(iter(DataLoader(dataset, batch_size=1, shuffle=True)))

    with torch.no_grad():
        features = sample['features'].to(device)
        targets = sample['targets'].cpu().numpy()[0]

        outputs = model(features)
        predicted = torch.argmax(outputs, dim=2).cpu().numpy()[0]

        # Преобразуем обратно в ID предметов
        predicted_items = [dataset.class_to_item[p] for p in predicted]
        true_items = [dataset.class_to_item.get(t, 0) for t in targets]

        print("\nПример предсказания:")
        print("Предсказанные предметы:", predicted_items)
        print("Реальные предметы:    ", true_items)
        print("Совпадения:          ", [p==t for p,t in zip(predicted_items, true_items)])

        # Визуализация
        plt.figure(figsize=(10, 4))
        plt.bar(range(9), predicted_items, width=0.4, label='Предсказано', align='center')
        plt.bar(np.arange(9)+0.4, true_items, width=0.4, label='Реально', align='center')
        plt.xticks(range(9), [f'Слот {i}' for i in range(9)])
        plt.ylabel('ID предмета')
        plt.legend()
        plt.title("Сравнение предсказанных и реальных предметов")
        plt.show()

if __name__ == "__main__":
    train_model()
