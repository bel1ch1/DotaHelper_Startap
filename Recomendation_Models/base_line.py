import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputClassifier
from sklearn.metrics import classification_report
from sklearn.preprocessing import StandardScaler

# Загрузка данных
df = pd.read_csv('match_dataset.csv')

# 1. Анализ доступных столбцов
print("Доступные столбцы в данных:")
print(df.columns.tolist())

# 2. Автоматическое определение признаков
# Ищем столбцы по паттернам
def find_columns_by_pattern(pattern):
    return [col for col in df.columns if pattern in col]

# Целевые переменные (предметы для рекомендации)
target_cols = find_columns_by_pattern('target_item_')
if not target_cols:
    raise ValueError("Не найдены целевые переменные target_item_*")

# Признаки
feature_cols = [col for col in df.columns if col not in target_cols]
print(f"\nИспользуется {len(feature_cols)} признаков")

# 3. Подготовка данных
X = df[feature_cols]
y = df[target_cols]

# 4. Обработка числовых признаков
numeric_cols = X.select_dtypes(include=['int64', 'float64']).columns.tolist()
print(f"\nЧисловые признаки ({len(numeric_cols)}):")
print(numeric_cols)

# 5. Разделение данных
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 6. Масштабирование только существующих числовых признаков
scaler = StandardScaler()
if numeric_cols:
    X_train[numeric_cols] = scaler.fit_transform(X_train[numeric_cols])
    X_test[numeric_cols] = scaler.transform(X_test[numeric_cols])

# 7. Обучение модели
model = MultiOutputClassifier(
    RandomForestClassifier(n_estimators=50, random_state=42, n_jobs=-1)
)
model.fit(X_train, y_train)

# 8. Оценка модели
y_pred = model.predict(X_test)
print("\nОценка модели:")
for i, col in enumerate(target_cols):
    print(f"\nОтчет для {col}:")
    print(classification_report(y_test[col], y_pred[:, i], zero_division=0))

# 9. Функция рекомендации
def recommend_items(game_context):
    """Рекомендует предметы на основе контекста игры"""
    # Фильтруем только существующие признаки
    valid_context = {k: v for k, v in game_context.items() if k in feature_cols}

    # Создаем DataFrame
    context_df = pd.DataFrame([valid_context])

    # Масштабируем числовые признаки
    if numeric_cols:
        context_df[numeric_cols] = scaler.transform(context_df[numeric_cols])

    # Предсказание
    predicted = model.predict(context_df)[0]

    # Возвращаем уникальные ненулевые предметы
    return [item for item in np.unique(predicted) if item != 0]

# 10. Пример использования
print("\nПример работы с реальными признаками из ваших данных:")
example_context = {
    col: df[col].iloc[2] for col in feature_cols  # Берем значения из первой строки
}
recommended_items = recommend_items(example_context)
print("Рекомендованные предметы:", recommended_items)
