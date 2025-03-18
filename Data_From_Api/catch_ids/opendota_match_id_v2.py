import requests
import time
import json

# Файл для сохранения match_id
output_file = "match_ids.txt"

# Функция для загрузки существующих match_id из файла
def load_existing_match_ids():
    try:
        with open(output_file, "r") as file:
            return set(json.load(file))
    except FileNotFoundError:
        return set()

# Функция для сохранения новых match_id в файл
def save_new_match_ids(new_match_ids):
    existing_match_ids = load_existing_match_ids()
    updated_match_ids = existing_match_ids.union(new_match_ids)

    with open(output_file, "w") as file:
        json.dump(list(updated_match_ids), file)

# Основной цикл
while True:
    # URL запроса
    url = "https://api.opendota.com/api/publicMatches"

    # Параметры запроса
    params = {
        "min_rank": 60,  # Минимальный рейтинг (7k)
        "limit": 100,     # Количество матчей (максимум 100)
    }

    # Отправка запроса
    response = requests.get(url, params=params)

    # Проверка успешности запроса
    if response.status_code == 200:
        matches = response.json()

        # Фильтрация матчей
        new_match_ids = set()
        for match in matches:
            # Проверяем, что game_mode = 22 (All Pick)
            if match.get("game_mode") == 22:
                # Проверяем, что 82 (Meepo) есть в radiant_team или dire_team
                if 82 in match.get("radiant_team", []) or 82 in match.get("dire_team", []):
                    new_match_ids.add(match["match_id"])

        # Загружаем существующие match_id
        existing_match_ids = load_existing_match_ids()

        # Находим новые match_id
        unique_new_match_ids = new_match_ids - existing_match_ids

        # Если есть новые match_id, сохраняем их в файл
        if unique_new_match_ids:
            print(f"Найдены новые Match ID: {unique_new_match_ids}")
            save_new_match_ids(unique_new_match_ids)
        else:
            print("Новых Match ID не найдено.")
    else:
        print("Ошибка:", response.status_code, response.text)

    # Пауза на 60 секунд перед следующим запросом
    time.sleep(60)
