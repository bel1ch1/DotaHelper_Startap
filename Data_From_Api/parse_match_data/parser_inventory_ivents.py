import json

class NewMatchParser:
    def __init__(self, json_data):
        self.data = json_data
        self.match_data = self.data.get('data', {}).get('match', {})
        self.players = self.match_data.get('players', [])
        self.duration = self.match_data.get('durationSeconds', 0)

        # Список разрешенных ID предметов противников
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

    def process_inventory(self):
        """Обрабатывает инвентарь всех игроков"""
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
        """Извлекает все предметы из события инвентаря"""
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
        Возвращает отфильтрованные предметы противников по этапам
        Только предметы из разрешенного списка
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

    def print_all_heroes(self):
        """Выводит список всех героев с их ID"""
        print("Доступные герои:")
        for hero_id, data in self.hero_items.items():
            print(f"ID: {hero_id}, Имя: {data['hero_name']}, Команда: {'Radiant' if data['isRadiant'] else 'Dire'}")

# Загрузка данных
path_to_json = 'match_data_v3.json'
with open(path_to_json, 'r') as f:
    new_data = json.load(f)

# Инициализация парсера
parser = NewMatchParser(new_data)

# Выводим список всех героев
parser.print_all_heroes()

# Запрашиваем ID героя пользователя
try:
    hero_id = int(input("\nВведите ID героя пользователя: "))

    # Получение предметов игрока
    player_items = parser.get_player_items(hero_id)
    print("\nПредметы игрока по этапам:")
    for group, items in player_items.items():
        print(f"{group}: {items}")

    # Получение отфильтрованных предметов противников
    enemy_items = parser.get_filtered_enemy_items(hero_id)
    print("\nОтфильтрованные предметы противников по этапам:")
    for group, items in enemy_items.items():
        print(f"{group}: {items}")
