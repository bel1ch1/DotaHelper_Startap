import os
import json
import time
import requests
from dotenv import load_dotenv


load_dotenv()
api_key = os.getenv('STRATZ_API_KEY')

# Настройки
INPUT_JSON = 'C:/work/DotaHelper_Startap/Data_From_Api/Data/not_dataset/meepo_ids.json'
OUTPUT_DIR = 'raw_matches'

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
        purchaseEvents {{
          time
          itemId
        }}
      }}
    }}
  }}
}}
"""

def fetch_match_data(match_id):
    """Загружает данные матча по API и сохраняет в JSON."""
    query = QUERY_TEMPLATE.format(match_id=match_id)
    response = requests.post(url, headers=headers, json={'query': query})

    if response.status_code == 200:
        data = response.json()
        filename = os.path.join(OUTPUT_DIR, f'match_{match_id}.json')
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Сохранён матч {match_id}")
    else:
        print(f"Ошибка при запросе матча {match_id}: {response.status_code}")

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
        time.sleep(1)

if __name__ == '__main__':
    main()
