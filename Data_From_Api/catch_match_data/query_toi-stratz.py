import os
from dotenv import load_dotenv
import requests
import json

# Загрузите переменные из .env файла
load_dotenv()

# Получите API-ключ из переменной окружения
api_key = os.getenv('STRATZ_API_KEY')

# URL API STRATZ GraphQL
url = 'https://api.stratz.com/graphql'

# Заголовки запроса
headers = {
    'Authorization': f'Bearer {api_key}',
    'User-Agent': 'STRATZ_API',  # Обязательный заголовок
    'Content-Type': 'application/json'  # Указываем, что отправляем JSON
}

# GraphQL-запрос
query = """
query{
  match(id: 8193325864){
    didRadiantWin
    durationSeconds
    radiantKills
    direKills
    players{
      isRadiant
      heroId
      hero{
        shortName
      }
      position
      playbackData{
        purchaseEvents{
          time
          itemId
        }
      }
    }
  }
}
"""

# Тело запроса
data = {
    'query': query
}

# Выполнение POST-запроса
try:
    response = requests.post(url, headers=headers, json=data)

    # Проверка статуса ответа
    if response.status_code == 200:
        # Если запрос успешен, получите данные
        match_data = response.json()

        # Сохраните данные в JSON файл
        filename = f'match_8193325864_data.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(match_data, f, ensure_ascii=False, indent=4)

        print(f"Данные о матче успешно сохранены в файл {filename}")
    else:
        # Если запрос не удался, выведите ошибку
        print(f"Ошибка: {response.status_code}")
        print(response.text)

except requests.exceptions.SSLError as e:
    print(f"Ошибка SSL: {e}")
except Exception as e:
    print(f"Произошла ошибка: {e}")
