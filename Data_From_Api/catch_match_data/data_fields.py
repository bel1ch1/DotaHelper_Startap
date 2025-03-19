'''
{
  match(id: 8193325864) {
    id                          # id матча
    didRadiantWin               # Кто победил
    durationSeconds             # Продолжительность
    towerStatusRadiant          # Оставшиеся тавера
    towerStatusDire             # Оставшиеся тавера
    barracksStatusRadiant       # Оставшиеся бараки
    barracksStatusDire          # Оставшиеся бараки
    lobbyType                   # Тип лобби
    gameMode                    # Тип игры
    isStats                     # Можно ли получить статистику
    actualRank                  # Ранг
    averageRank                 # Ранг
    averageImp                  # Импакт
    gameVersionId               # Версия игры
    regionId                    # Регион
    rank                        # Ранг
    analysisOutcome             # Вариант исхода матча
    predictedOutcomeWeight      # Уверенность модели в предсказании
    players {                   # данные об игроках
      heroId                    # герой
      kills                     # k
      deaths                    # d
      assists                   # a
    }
    radiantNetworthLeads        # Приемущество Radiant
    radiantExperienceLeads      # Приемущество Radiant
    radiantKills                # Килы на каждую минуту
    direKills                   # Килы на каждую минуту
    pickBans {                  # Стадия дравфта
      isPick                    # пикнут
      heroId                    # герой
      order                     # какой в последовательности
    }
    winRates                    # вероятность победы Radiant per minut
    predictedWinRates           # вероятность победы Radiant per minut
    bottomLaneOutcome           # исход лайна
    midLaneOutcome              # исход лайна
    topLaneOutcome              # исход лайна
    didRequestDownload
  }
}
'''
