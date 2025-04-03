import os
import json
import time
import requests
from dotenv import load_dotenv


load_dotenv()
api_key = os.getenv('STRATZ_API_KEY')

# Настройки
INPUT_JSON = 'C:/work/DotaHelper_Startap/Data_From_Api/Data/not_dataset/meepo_test_ids.json'
OUTPUT_DIR = 'raw_test_matches'

os.makedirs(OUTPUT_DIR, exist_ok=True)

url = 'https://api.stratz.com/graphql'
headers = {
    'Authorization': f'Bearer {api_key}',
    'User-Agent': 'STRATZ_API',
    'Content-Type': 'application/json'
}


QUERY_TEMPLATE = """
query {{
  match(id: {match_id}) {{
    didRadiantWin
    durationSeconds
    radiantKills
    direKills
    players {{
      isRadiant
      heroId
      hero {{
        shortName
      }}
      position
      playbackData {{
        inventoryEvents{{
          time
          item0{{itemId}}
          item1{{itemId}}
          item2{{itemId}}
          item3{{itemId}}
          item4{{itemId}}
          item5{{itemId}}
          backPack0{{itemId}}
          backPack1{{itemId}}
          backPack2{{itemId}}
        }}
      }}
    }}
  }}
}}
"""

def fetch_match_data(match_id, max_retries=3):
    """Загружает данные матча по API и сохраняет в JSON."""
    for attempt in range(max_retries):
        try:
            query = QUERY_TEMPLATE.format(match_id=match_id)
            response = requests.post(url, headers=headers, json={'query': query})
            response.raise_for_status()  # Проверяем на HTTP ошибки

            data = response.json()

            # Проверяем наличие ошибок в ответе GraphQL
            if 'errors' in data:
                print(f"GraphQL ошибка в матче {match_id}: {data['errors']}")
                time.sleep(1)
                continue

            filename = os.path.join(OUTPUT_DIR, f'match_{match_id}.json')
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Сохранён матч {match_id}")
            return True

        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе матча {match_id} (попытка {attempt + 1}/{max_retries}): {str(e)}")
            time.sleep(1)  # Задержка перед повторной попыткой
        except Exception as e:
            print(f"Неожиданная ошибка при обработке матча {match_id}: {str(e)}")
            time.sleep(1)
            return False

    print(f"Не удалось загрузить матч {match_id} после {max_retries} попыток")
    return False

def main():
    # Загружаем список matchId из JSON-файла
    with open(INPUT_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Извлекаем все matchId (пример структуры: data -> heroStats -> guide -> guides -> matchId)
    match_ids = []
    for guide in data['data']['heroStats']['guide']:
        for g in guide['guides']:
            match_ids.append(g['matchId'])

    # Загружаем данные для каждого матча
    for match_id in match_ids:
        fetch_match_data(match_id)
        time.sleep(1)  # Базовая задержка между запросами

if __name__ == '__main__':
    main()
