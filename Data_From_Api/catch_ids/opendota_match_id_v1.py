import requests

# URL запроса
url = "https://api.opendota.com/api/publicMatches"

# Параметры запроса
params = {
    "min_rank": 70,
    "limit": 100,
}

# Отправка запроса
response = requests.get(url, params=params)

# Проверка успешности запроса
if response.status_code == 200:
    matches = response.json()

    # Фильтрация матчей
    filtered_matches = []
    for match in matches:
        # Проверяем, что game_mode = 22 (All Pick)
        if match.get("game_mode") == 22:
            # Проверяем, что 82 (Meepo) есть в radiant_team или dire_team
            if 82 in match.get("radiant_team", []) or 82 in match.get("dire_team", []):
                filtered_matches.append(match["match_id"])

    # Вывод результатов
    print("Отфильтрованные Match ID:", filtered_matches)
else:
    print("Ошибка:", response.status_code, response.text)
