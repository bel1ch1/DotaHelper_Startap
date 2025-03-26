import json


# Загрузка JSON
path_to_data = 'match_8227173818_data.json'
with open(path_to_data, 'r') as f:
    data = json.load(f)


class MatchParser:
    def __init__(self, json_data):
        """
        Initialization of a class with json data loading.
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
        Separation of players into teams Radiant and Dire.
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


    def group_items_by_time(self):
        time_intervals = [
            (-300, 360),   # Группа 0
            (360, 900),    # Группа 1
            (900, 1500),    # Группа 2
            (1500, 2100),   # Группа 3
            (2100, 2700),   # Группа 4
            (2700, 3600),   # Группа 5
            (3600, float('inf'))  # Группа 6
        ]

        for player in self.players:
            short_name = player.get("hero", {}).get("shortName", "unknown")
            playback_data = player.get("playbackData", {})
            purchase_events = playback_data.get("purchaseEvents", [])

            if short_name not in self.hero_items:
                # Инициализируем все группы как None
                self.hero_items[short_name] = {f"group_{i}": None for i in range(len(time_intervals))}

            for event in purchase_events:
                time = event.get("time", 0)
                item_id = event.get("itemId", "unknown")

                for i, (start, end) in enumerate(time_intervals):
                    if start <= time < end:
                        # Если группа еще не инициализирована, создаем пустой список
                        if self.hero_items[short_name][f"group_{i}"] is None:
                            self.hero_items[short_name][f"group_{i}"] = []

                        # Добавляем предмет в текущую и все последующие группы
                        for j in range(i, len(time_intervals)):
                            if end > self.durationSeconds:
                                # Если временной интервал выходит за пределы матча, пропускаем
                                continue
                            if self.hero_items[short_name][f"group_{j}"] is None:
                                self.hero_items[short_name][f"group_{j}"] = []
                            self.hero_items[short_name][f"group_{j}"].append(item_id)
                        break

        # Помечаем группы, выходящие за пределы матча, как None
        for hero in self.hero_items.values():
            for i in range(len(time_intervals)):
                start, end = time_intervals[i]
                if start >= self.durationSeconds:
                    hero[f"group_{i}"] = None


    def get_match_data(self):
        '''
        Return:
        Who win: [0]
        The duration of the match in seconds: [1]
        '''
        if self.didRadiantWin is True:
            win = 'Radiant'
        else:
            win = 'Dire'
        return [win, self.durationSeconds]


    def get_sorted_heroes(self):
        """
        Sorted vectors for each team:
        radiant: [0]
        dire: [1]
        """
        return self.radiant_heroes, self.dire_heroes


    def get_kills_advantage_per_stage(self, radiant, dire):
        """
        Returns the vector of advantages for each stage if it has reached it
        """
        result = []
        n = len(radiant)
        group_0 = []
        group_1 = []
        group_2 = []
        group_3 = []
        group_4 = []
        group_5 = []
        group_6 = []
        for i in range(n-1):
            res = radiant[i] - dire[i]
            if i <= 5:
                group_0.append(res)
            elif i >= 6 and i <= 15:
                group_1.append(res)
            elif i >= 16 and i <= 25:
                group_2.append(res)
            elif i >= 26 and i <= 35:
                group_3.append(res)
            elif i >= 36 and i <= 45:
                group_4.append(res)
            elif i >= 46 and i <= 60:
                group_5.append(res)
            elif i > 60:
                group_6.append(res)
        if group_0:
          result.append(sum(group_0))
        if group_1:
          result.append(sum(group_1))
        if group_2:
          result.append(sum(group_2))
        if group_3:
          result.append(sum(group_3))
        if group_4:
          result.append(sum(group_4))
        if group_5:
          result.append(sum(group_5))
        if group_6:
          result.append(sum(group_6))

        return result


    def get_hero_items(self):
        """
        Returns grouping items for each hero
        """
        return self.hero_items


    def get_player_items(self, hero_id):
        """
        Возвращает все предметы указанного героя (по heroId) для всех стадий, где они не None
        Формат: {group_0: [item1, item2], group_1: [item3, ...], ...}
        """
        hero_items = {}

        # Находим героя по heroId
        player_hero = None
        for player in self.players:
            if player.get('heroId') == hero_id:
                player_hero = player.get('hero', {}).get('shortName')
                break

        if not player_hero:
            return {}

        # Собираем все не-None группы предметов
        for group, items in self.hero_items.get(player_hero, {}).items():
            if items is not None:
                hero_items[group] = items

        return hero_items

    def get_enemy_items(self, hero_id):
        """
        Возвращает все предметы противников указанного героя (по heroId)
        для всех стадий, где они не None
        Формат: {hero_name: {group_0: [item1, ...], ...}, ...}
        """
        enemy_items = {}

        # Определяем команду героя
        is_radiant = None
        for player in self.players:
            if player.get('heroId') == hero_id:
                is_radiant = player.get('isRadiant', False)
                break

        if is_radiant is None:
            return {}

        # Собираем предметы всех противников
        for player in self.players:
            if player.get('isRadiant', False) != is_radiant:  # Игрок из противоположной команды
                hero_name = player.get('hero', {}).get('shortName')
                hero_data = {}

                for group, items in self.hero_items.get(hero_name, {}).items():
                    if items is not None:
                        hero_data[group] = items

                if hero_data:  # Добавляем только если есть предметы
                    enemy_items[hero_name] = hero_data

        return enemy_items


parser = MatchParser(data)
parser.process_players()
parser.group_items_by_time()

match_data = parser.get_match_data()
print("Match Data:", match_data)

radiant_heroes, dire_heroes = parser.get_sorted_heroes()
print("Radiant Heroes:", radiant_heroes)
print("Dire Heroes:", dire_heroes)

kills_advantage = parser.get_kills_advantage_per_stage(parser.radiantKills, parser.direKills)
print("Kills Advantage:", kills_advantage)

hero_items = parser.get_hero_items()
player_items = parser.get_player_items(82)
print("Player items:", player_items)
enemy_items = parser.get_enemy_items(82)
print("Enemy items:", enemy_items)
