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
{
  match(id: 8193325864) {
    id
    didRadiantWin # Кто победил
    durationSeconds # Продолжительность
    towerStatusRadiant # Оставшиеся тавера
    towerStatusDire # Оставшиеся тавера
    barracksStatusRadiant # Оставшиеся бараки
    barracksStatusDire  # Оставшиеся бараки
    lobbyType
    gameMode
    isStats # Можно ли получить статистику
    actualRank # Ранг
    averageRank # Ранг
    averageImp # Импакт
    gameVersionId
    regionId
    rank  # Ранг
    analysisOutcome # Вариант исхода матча
    predictedOutcomeWeight # Уверенность модели в предсказании
    players {
      heroId
      playerSlot
      kills
      deaths
      assists
      goldPerMinute
      experiencePerMinute
      networth
      heroDamage
      towerDamage
      heroHealing
      position
      role
      streakPrediction
      imp
      award
      behavior
      stats{
     	  itemPurchases{
          itemId
          time
        }
        inventoryReport{
          item0{
            itemId
          }
          item1{
            itemId
          }
          item2{
            itemId
          }
          item3{
            itemId
          }
          item4{
            itemId
          }
          item5{
            itemId
          }
          backPack0{
            itemId
          }
          backPack1{
            itemId
          }
          backPack2{
            itemId
          }
          neutral0{
            itemId
          }
        }
      }
      item0Id
      item1Id
      item2Id
      item3Id
      item4Id
      item5Id
      backpack0Id
      backpack1Id
      backpack2Id
      neutral0Id
    }
    radiantNetworthLeads # Приемущество Radiant
    radiantExperienceLeads # Приемущество Radiant
    radiantKills # Килы на каждую минуту
    direKills  # Килы на каждую минуту
    pickBans {
      isPick
      heroId
      order
    }
    winRates # вероятность победы Radiant per minut
    predictedWinRates # вероятность победы Radiant per minut
    bottomLaneOutcome # исход лайна
    midLaneOutcome # исход лайна
    topLaneOutcome # исход лайна
    didRequestDownload
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
