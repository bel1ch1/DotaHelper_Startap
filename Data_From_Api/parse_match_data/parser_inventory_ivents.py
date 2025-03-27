import json


class NewMatchParser:
    def __init__(self, json_data):
        self.data = json_data
        self.match_data = self.data.get('data', {}).get('match', {})
        self.players = self.match_data.get('players', [])
        self.duration = self.match_data.get('durationSeconds', 0)
        self.radiantKills = self.data.get('data', {}).get('match', {}).get('radiantKills', [])
        self.direKills = self.data.get('data', {}).get('match', {}).get('direKills', [])

        # List of IDs allowed opponent items
        self.allowed_item_ids = [
            37, 40, 96, 98, 100, 102, 104, 119, 127, 139,
            152, 156, 160, 176, 204, 206, 208, 210, 249,
            250, 254, 267, 598, 610, 911, 1107, 1466, 1806, 1808
        ]

        self.time_intervals = [
            (-300, 360),    # Группа 0
            (360, 900),     # Группа 1
            (900, 1500),    # Группа 2
            (1500, 2100),   # Группа 3
            (2100, 2700),   # Группа 4
            (2700, 3600),   # Группа 5
            (3600, float('inf'))  # Группа 6
        ]

        self.hero_items = {}
        self.process_inventory()


    def get_winner(self):
        """
        Defines the winning team of the match

        Returns:
            str: 'Radiant' or 'Dire'
        """
        did_radiant_win = self.match_data.get('didRadiantWin')

        if did_radiant_win is True:
            return 'Radiant'
        else:
            return 'Dire'


    def get_player_result(self, hero_id):
        """
        Определяет результат матча для конкретного игрока

        Args:
            hero_id (int): ID героя игрока

        Returns:
            str: 'win' если игрок в победившей команде,
                'lose' если игрок в проигравшей команде,
                'unknown' если результат не определен или герой не найден
        """
        if hero_id not in self.hero_items:
            return 'unknown'

        # Определяем победителя матча
        match_winner = 'Radiant' if self.match_data.get('didRadiantWin') else 'Dire'

        # Определяем команду игрока
        player_team = 'Radiant' if self.hero_items[hero_id]['isRadiant'] else 'Dire'

        return 'win' if player_team == match_winner else 'lose'


    def process_inventory(self):
        """ Processed inventorys of the all players """
        for player in self.players:
            hero_id = player.get('heroId')
            if hero_id is None:
                continue

            if hero_id not in self.hero_items:
                self.hero_items[hero_id] = {
                    'isRadiant': player.get('isRadiant'),
                    'hero_name': player.get('hero', {}).get('shortName', 'unknown'),
                    'items': {f'group_{i}': set() for i in range(len(self.time_intervals))}
                }

            playback_data = player.get('playbackData', {})
            if not playback_data:
                continue

            events = playback_data.get('inventoryEvents', [])
            for event in events:
                if not event:
                    continue

                time = event.get('time', 0)
                items = self.extract_items_from_event(event)

                for i, (start, end) in enumerate(self.time_intervals):
                    if start <= time < end:
                        self.hero_items[hero_id]['items'][f'group_{i}'].update(items)
                        break


    def extract_items_from_event(self, event):
        """ Extract items from inventory events"""
        items = set()
        if not event:
            return items

        for slot in ['item0', 'item1', 'item2', 'item3', 'item4', 'item5',
                    'backPack0', 'backPack1', 'backPack2']:
            slot_data = event.get(slot)
            if slot_data and isinstance(slot_data, dict):
                item_id = slot_data.get('itemId')
                if item_id:
                    items.add(item_id)
        return items


    def get_player_items(self, hero_id):
        """Возвращает предметы игрока по этапам"""
        if hero_id not in self.hero_items:
            return {}

        return {
            group: list(items)
            for group, items in self.hero_items[hero_id]['items'].items()
            if items
        }


    def get_filtered_enemy_items(self, hero_id):
        """
        Returns filtred enemy items for each stage
        """
        if hero_id not in self.hero_items:
            return {}

        player_team = self.hero_items[hero_id]['isRadiant']
        enemy_items = {f'group_{i}': set() for i in range(len(self.time_intervals))}

        for p_id, data in self.hero_items.items():
            if data['isRadiant'] != player_team:  # Противник
                for group, items in data['items'].items():
                    filtered = {item for item in items if item in self.allowed_item_ids}
                    enemy_items[group].update(filtered)

        return {
            group: list(items)
            for group, items in enemy_items.items()
            if items
        }


    def get_enemy_team_ids(self, hero_id):
        """
        Возвращает список ID героев команды противников
        для указанного героя (по его hero_id)

        Args:
            hero_id (int): ID героя, для которого ищем противников

        Returns:
            list: Список ID героев противников или пустой список, если hero_id не найден
        """
        if hero_id not in self.hero_items:
            return []

        player_team = self.hero_items[hero_id]['isRadiant']
        enemy_ids = []

        for p_id, data in self.hero_items.items():
            if data['isRadiant'] != player_team:  # Это противник
                enemy_ids.append(p_id)

        return enemy_ids


    def print_all_heroes(self):
        """Выводит список всех героев с их ID"""
        print("Доступные герои:")
        for hero_id, data in self.hero_items.items():
            print(f"ID: {hero_id}, Имя: {data['hero_name']}, Команда: {'Radiant' if data['isRadiant'] else 'Dire'}")


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
        self.advantage = result
        return result


    def stage_winner(self, result):
        """
        Returns the winner for each stage.

        Radiant: 1
        Dire: 0
        """
        stage_winner = []
        for i in range(len(result)):
            if result[i] >= 0:
                stage_winner.append(1)
            else:
                stage_winner.append(0)
        return stage_winner



path_to_json = 'match_data_v3.json'
with open(path_to_json, 'r') as f:
    new_data = json.load(f)


parser = NewMatchParser(new_data)

# Printing all heroes
parser.print_all_heroes()

hero_id = int(input("\nВведите ID героя пользователя: "))

winner = parser.get_winner()
print(f"\nПобедитель матча: {winner}")

result = parser.get_player_result(hero_id)
print(f"\nUser victory status: {result}")

kills_advantage = parser.get_kills_advantage_per_stage(parser.radiantKills, parser.direKills)
print("Kills Advantage:", kills_advantage)

st_winner = parser.stage_winner(parser.advantage)
print(f'Stage Winner: {st_winner}')

enemy_ids = parser.get_enemy_team_ids(hero_id)
print(f"\nID героев противников: {enemy_ids}")

# user items
player_items = parser.get_player_items(hero_id)
print("\nПредметы игрока по этапам:")
for group, items in player_items.items():
    print(f"{group}: {items}")

# enemy items
enemy_items = parser.get_filtered_enemy_items(hero_id)
print("\nОтфильтрованные предметы противников по этапам:")
for group, items in enemy_items.items():
    print(f"{group}: {items}")
