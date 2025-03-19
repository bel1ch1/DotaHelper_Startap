import requests
import time
import json
import os

# Название файла для сохранения match_id
output_file = "match_ids_v2.json"

# Функция для загрузки существующих match_id из файла
def load_existing_match_ids():
    # Проверяем, существует ли файл
    if not os.path.exists(output_file):
        # Если файл не существует, создаём пустой JSON-объект
        with open(output_file, "w") as file:
            json.dump({}, file)
        return {}

    # Если файл существует, загружаем данные
    try:
        with open(output_file, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        # Если файл повреждён, создаём новый
        print("Ошибка: Файл содержит некорректный JSON. Создаю новый файл.")
        with open(output_file, "w") as file:
            json.dump({}, file)
        return {}

# Функция для сохранения новых match_id в файл
def save_new_match_ids(new_match_ids):
    # Загружаем существующие данные
    existing_data = load_existing_match_ids()

    # Добавляем новые match_id с текущей временной меткой
    current_timestamp = time.time()  # Текущая временная метка в секундах
    for match_id in new_match_ids:
        existing_data[str(match_id)] = current_timestamp  # Ключи JSON должны быть строками

    # Сохраняем обновлённые данные в файл
    with open(output_file, "w") as file:
        json.dump(existing_data, file, indent=4)

# Основной цикл
while True:
    # URL запроса
    url = "https://api.opendota.com/api/publicMatches"

    # Параметры запроса
    params = {
        "min_rank": 60,  # Минимальный рейтинг (6k)
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

        # Загружаем существующие данные
        existing_data = load_existing_match_ids()

        # Находим новые match_id
        unique_new_match_ids = new_match_ids - set(map(int, existing_data.keys()))  # Преобразуем ключи в int для сравнения

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
