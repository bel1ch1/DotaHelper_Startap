import json

path_to_data = 'match_data.json'

# Загрузка JSON
with open(path_to_data, 'r') as f:
    data = json.load(f)

class MatchParser:
    def __init__(self, json_data):
        """
        Инициализация класса с загрузкой JSON данных.
        """
        self.data = json_data
        self.players = self.data.get('data', {}).get('match', {}).get('players', [])
        self.radiantKills = self.data.get('data', {}).get('match', {}).get('radiantKills', [])
        self.direKills = self.data.get('data', {}).get('match', {}).get('direKills', [])
        self.didRadiantWin = self.data.get('data', {}).get('match', {}).get('didRadiantWin', False)
        self.durationSeconds = self.data.get('data', {}).get('match', {}).get('durationSeconds', 0)
        self.radiant_heroes = []
        self.dire_heroes = []
        self.position_order = {
            "POSITION_1": 1,
            "POSITION_2": 2,
            "POSITION_3": 3,
            "POSITION_4": 4,
            "POSITION_5": 5
        }
        self.hero_items = {}  # Словарь для хранения предметов по героям

    def process_players(self):
        """
        Разделение игроков на команды Radiant и Dire.
        """
        # Создаем списки героев и сортируем их по позициям
        self.radiant_heroes = sorted(
            [
                {"shortName": player["hero"]["shortName"], "position": player["position"], "heroId": player["heroId"]}
                for player in self.players
                if player.get("isRadiant", False)
            ],
            key=lambda x: self.position_order[x["position"]]
        )

        self.dire_heroes = sorted(
            [
                {"shortName": player["hero"]["shortName"], "position": player["position"], "heroId": player["heroId"]}
                for player in self.players
                if not player.get("isRadiant", True)
            ],
            key=lambda x: self.position_order[x["position"]]
        )

    def get_match_data(self):
        '''
        Получение данных:
        Кто победил: [0]
        Продолжительность матча в секундах: [1]
        '''
        return [self.didRadiantWin, self.durationSeconds]

    def get_sorted_heroes(self):
        """
        Получение отсортированных списков героев для обеих команд:
        radiant: [0]
        dire: [1]
        """
        return self.radiant_heroes, self.dire_heroes

    def get_kills_advantage_per_minute(self, radiant, dire):
        """
        Метод вычисляет разницу по фрагам за каждую минуту матча.
        """
        status = []
        for i in range(len(radiant)):
            res = radiant[i] - dire[i]
            status.append(res)
        return status

    def group_items_by_time(self):
        """
        Группирует предметы по временным интервалам для каждого героя.
        Предметы из предыдущих групп добавляются в последующие.
        """
        # Временные интервалы (в секундах)
        time_intervals = [
            (-300, 360),  # Группа 0
            (360, 900),   # Группа 1
            (900, 1500),  # Группа 2
            (1500, 2100), # Группа 3
            (2100, 2700), # Группа 4
            (2700, 3600), # Группа 5
            (3600, float('inf'))  # Группа 6
        ]

        for player in self.players:
            short_name = player.get("hero", {}).get("shortName", "unknown")  # Используем shortName вместо heroId
            playback_data = player.get("playbackData", {})
            purchase_events = playback_data.get("purchaseEvents", [])

            # Инициализация списков для каждого временного интервала, если они еще не созданы
            if short_name not in self.hero_items:
                self.hero_items[short_name] = {f"group_{i}": [] for i in range(len(time_intervals))}

            for event in purchase_events:
                time = event.get("time", 0)
                item_id = event.get("itemId", "unknown")

                # Определяем, в какую группу попадает предмет
                for i, (start, end) in enumerate(time_intervals):
                    if start <= time < end:
                        # Добавляем предмет в текущую и все последующие группы
                        for j in range(i, len(time_intervals)):
                            self.hero_items[short_name][f"group_{j}"].append(item_id)
                        break

    def get_hero_items(self):
        """
        Возвращает группированные предметы для каждого героя.
        """
        return self.hero_items


parser = MatchParser(data)
parser.process_players()
parser.group_items_by_time()


match_data = parser.get_match_data()
print("Match Data:", match_data)

radiant_heroes, dire_heroes = parser.get_sorted_heroes()
print("Radiant Heroes:", radiant_heroes)
print("Dire Heroes:", dire_heroes)

kills_advantage = parser.get_kills_advantage_per_minute(parser.radiantKills, parser.direKills)
print("Kills Advantage:", kills_advantage)

hero_items = parser.get_hero_items()
for short_name, items in hero_items.items():
    print(f"Hero {short_name}:")
    for group, item_list in items.items():
        print(f"  {group}: {item_list}")
