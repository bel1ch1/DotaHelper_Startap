import json


class NewMatchParser:
    def __init__(self, json_data):
        self.data = json_data
        self.match_data = self.data.get('data', {}).get('match', {})
        self.players = self.match_data.get('players', [])
        self.duration = self.match_data.get('durationSeconds', 0)
        self.radiantKills = self.data.get('data', {}).get('match', {}).get('radiantKills', [])
        self.direKills = self.data.get('data', {}).get('match', {}).get('direKills', [])

        # Обновленный список разрешенных ID предметов пользователя (только ключи)
        self.allowed_player_item_ids = {
            1, 2, 6, 7, 11, 12, 13, 14, 15, 16, 20, 25, 26, 27, 28, 29, 30, 31, 32, 34,
            36, 37, 38, 39, 40, 41, 42, 48, 50, 56, 63, 65, 73, 75, 77, 79, 81, 88, 90,
            92, 94, 96, 98, 100, 102, 104, 108, 110, 112, 114, 116, 119, 121, 123, 125,
            127, 133, 135, 137, 139, 141, 143, 145, 147, 149, 151, 152, 154, 156, 158,
            160, 162, 164, 166, 168, 170, 172, 174, 176, 178, 180, 181, 185, 190, 196,
            206, 208, 210, 214, 216, 220, 223, 225, 226, 229, 231, 232, 235, 236, 237,
            242, 244, 247, 249, 250, 252, 254, 256, 259, 261, 263, 265, 267, 269, 273,
            277, 473, 534, 596, 598, 600, 603, 604, 609, 610, 635, 692, 911, 931, 939,
            964, 1097, 1107, 1123, 1128, 1466, 1575, 1806
        }

        # Список разрешенных ID предметов противников (оставьте ваш текущий)
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
        """Извлекает предметы из события инвентаря с фильтрацией"""
        items = set()
        if not event:
            return items

        for slot in ['item0', 'item1', 'item2', 'item3', 'item4', 'item5',
                    'backPack0', 'backPack1', 'backPack2']:
            slot_data = event.get(slot)
            if slot_data and isinstance(slot_data, dict):
                item_id = slot_data.get('itemId')
                # Проверяем принадлежность к разрешенным предметам
                if item_id is not None and item_id in self.allowed_player_item_ids:
                    items.add(item_id)
        return items


    def get_player_items(self, hero_id):
        """Возвращает ID предметов игрока по этапам (только разрешенные)"""
        if hero_id not in self.hero_items:
            return {}

        return {
            group: sorted(list(items))  # Сортировка ID для удобства
            for group, items in self.hero_items[hero_id]['items'].items()
            if items  # Исключаем пустые группы
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
        user_team_ids = []
        for p_id, data in self.hero_items.items():
            if data['isRadiant'] != player_team:  # Это противник
                enemy_ids.append(p_id)
            else:
                if p_id != hero_id:
                    user_team_ids.append(p_id)

        return enemy_ids, user_team_ids


    def print_all_heroes(self):
        """Выводит список всех героев с их ID"""
        print("Доступные герои:")
        for hero_id, data in self.hero_items.items():
            print(f"ID: {hero_id}, Имя: {data['hero_name']}, Команда: {'Radiant' if data['isRadiant'] else 'Dire'}")


    def get_kills_advantage_per_stage(self, hero_id):
        """
        Returns kill advantage for each stage relative to player's team

        Args:
            hero_id (int): ID of the player's hero

        Returns:
            list: Kill advantage per stage where:
                positive values = player's team advantage
                negative values = enemy team advantage
                None if hero not found
        """
        if hero_id not in self.hero_items:
            return None

        result = []
        player_is_radiant = self.hero_items[hero_id]['isRadiant']
        n = min(len(self.radiantKills), len(self.direKills))

        group_0 = []
        group_1 = []
        group_2 = []
        group_3 = []
        group_4 = []
        group_5 = []
        group_6 = []

        for i in range(n):
            # Calculate advantage from player's team perspective
            if player_is_radiant:
                advantage = self.radiantKills[i] - self.direKills[i]
            else:
                advantage = self.direKills[i] - self.radiantKills[i]

            # Group by time intervals
            if i <= 5:
                group_0.append(advantage)
            elif 6 <= i <= 15:
                group_1.append(advantage)
            elif 16 <= i <= 25:
                group_2.append(advantage)
            elif 26 <= i <= 35:
                group_3.append(advantage)
            elif 36 <= i <= 45:
                group_4.append(advantage)
            elif 46 <= i <= 60:
                group_5.append(advantage)
            elif i > 60:
                group_6.append(advantage)

        # Calculate average advantage per stage
        if group_0:
            result.append(sum(group_0)/len(group_0))
        if group_1:
            result.append(sum(group_1)/len(group_1))
        if group_2:
            result.append(sum(group_2)/len(group_2))
        if group_3:
            result.append(sum(group_3)/len(group_3))
        if group_4:
            result.append(sum(group_4)/len(group_4))
        if group_5:
            result.append(sum(group_5)/len(group_5))
        if group_6:
            result.append(sum(group_6)/len(group_6))

        self.advantage = result
        return result


    def stage_winner(self, hero_id):
        """
        Determine stage winners from player's perspective

        Args:
            hero_id (int): ID of the player's hero

        Returns:
            list: 1 if player's team won the stage
                0 if enemy team won the stage
                None if hero not found
        """
        if hero_id not in self.hero_items:
            return None

        advantage = self.get_kills_advantage_per_stage(hero_id)
        if advantage is None:
            return None

        return [1 if adv >= 0 else 0 for adv in advantage]


class MatchStatsAnalyzer:
    def __init__(self, match_parser, vs_file_path, with_file_path, win_rate_file_path):
        """
        Инициализирует анализатор статистики матча
        Args:
            match_parser (NewMatchParser): экземпляр парсера матча
            vs_file_path (str): путь к файлу с винрейтами против врагов
            with_file_path (str): путь к файлу с винрейтами с союзниками
            win_rate_file_path (str): путь к файлу с общей статистикой героев
        """
        self.parser = match_parser
        self.vs_data = self._load_json_file(vs_file_path)
        self.with_data = self._load_json_file(with_file_path)
        self.win_rate_data = self._load_json_file(win_rate_file_path)

    def _load_json_file(self, file_path):
        """Загружает JSON файл"""
        with open(file_path, 'r') as f:
            return json.load(f)

    def _find_hero_matchup(self, hero_id, hero_id2, matchup_data, matchup_type='vs'):
        """
        Ищет винрейт героя против другого героя или с союзником
        Args:
            hero_id (int): ID основного героя
            hero_id2 (int): ID героя противника/союзника
            matchup_data (dict): данные о матчапах
            matchup_type (str): 'vs' для противников, 'with' для союзников

        Returns:
            float: винрейт или 0.5 если данные не найдены
        """
        hero_stats = matchup_data.get('data', {}).get('heroStats', {})
        matchups = hero_stats.get('matchUp', [])

        for matchup in matchups:
            if matchup.get('heroId') == hero_id:
                relations = matchup.get(matchup_type, [])
                for rel in relations:
                    if rel.get('heroId2') == hero_id2:
                        return rel.get('winsAverage', 0.5)

        # Возвращаем 0.5 если данных нет (нейтральный винрейт)
        return 0.5


    def get_enemy_win_rates(self, hero_id):
        """
        Возвращает винрейты героя пользователя против каждого героя противника

        Args:
            hero_id (int): ID героя пользователя

        Returns:
            list: список из 5 винрейтов против героев противника
        """
        enemy_ids, _ = self.parser.get_enemy_team_ids(hero_id)
        win_rates = []

        for enemy_id in enemy_ids:
            win_rate = self._find_hero_matchup(hero_id, enemy_id, self.vs_data, 'vs')
            win_rates.append(win_rate)

        return win_rates


    def get_ally_win_rates(self, hero_id):
        """
        Возвращает винрейты героя пользователя с каждым героем союзника

        Args:
            hero_id (int): ID героя пользователя

        Returns:
            list: список из 4 винрейтов с героями союзников
        """
        _, ally_ids = self.parser.get_enemy_team_ids(hero_id)
        win_rates = []

        for ally_id in ally_ids:
            win_rate = self._find_hero_matchup(hero_id, ally_id, self.with_data, 'with')
            win_rates.append(win_rate)

        return win_rates


    def _get_hero_win_rate(self, hero_id):
        """
        Получает общий винрейт героя по его ID

        Args:
            hero_id (int): ID героя

        Returns:
            float: винрейт героя или 0.5 если данные не найдены
        """
        hero_stats = self.win_rate_data.get('data', {}).get('heroStats', {})
        win_rates = hero_stats.get('winGameVersion', [])

        for hero in win_rates:
            if hero.get('heroId') == hero_id:
                match_count = hero.get('matchCount', 1)
                win_count = hero.get('winCount', 0)
                return win_count / match_count if match_count > 0 else 0.5

        return 0.5  # Возвращаем нейтральный винрейт если герой не найден


    def calculate_team_win_rates(self, hero_id):
        """
        Вычисляет суммарные винрейты команд пользователя и противников

        Args:
            hero_id (int): ID героя пользователя

        Returns:
            tuple: (суммарный винрейт команды пользователя, суммарный винрейт команды противников)
        """
        enemy_ids, ally_ids = self.parser.get_enemy_team_ids(hero_id)

        # Получаем винрейт героя пользователя
        user_win_rate = self._get_hero_win_rate(hero_id)

        # Вычисляем винрейт команды пользователя (герой пользователя + 4 союзника)
        user_team_total = user_win_rate
        for ally_id in ally_ids:
            user_team_total += self._get_hero_win_rate(ally_id)

        # Вычисляем винрейт команды противников (5 героев)
        enemy_team_total = 0
        for enemy_id in enemy_ids:
            enemy_team_total += self._get_hero_win_rate(enemy_id)

        return user_team_total, enemy_team_total


    def get_team_advantage(self, hero_id):
        """
        Определяет преимущество команды пользователя над командой противников

        Args:
            hero_id (int): ID героя пользователя

        Returns:
            float: разница винрейтов (user_team - enemy_team)
                положительное значение - преимущество пользователя
                отрицательное - преимущество противников
        """
        user_total, enemy_total = self.calculate_team_win_rates(hero_id)

        return user_total - enemy_total


 # file paths
match_file_path = 'C:/work/DotaHelper_Startap/Data_From_Api/Data/not_dataset/match_data_v3.json'
vs_file_path = 'C:/work/DotaHelper_Startap/Data_From_Api/Data/not_dataset/meepo_matchup_vs.json'
with_file_path = 'C:/work/DotaHelper_Startap/Data_From_Api/Data/not_dataset/meepo_matchup_with.json'
win_rate_file_path = 'C:/work/DotaHelper_Startap/Data_From_Api/Data/not_dataset/win_data_for_all.json'


with open(match_file_path, 'r') as f:
    match_data = json.load(f)


parser = NewMatchParser(match_data)
analyzer = MatchStatsAnalyzer(parser, vs_file_path, with_file_path, win_rate_file_path)

hero_id = 82

# teams
enemy_ids, user_team_ids = parser.get_enemy_team_ids(hero_id)
print(f"\nID героев противников: {enemy_ids}")
print(f"\nID героев союзников: {user_team_ids}")

# user items
# winrates
enemy_win_rates = analyzer.get_enemy_win_rates(hero_id)
ally_win_rates = analyzer.get_ally_win_rates(hero_id)
user_team_total, enemy_team_total = analyzer.calculate_team_win_rates(hero_id)
team_advantage = analyzer.get_team_advantage(hero_id)
# advantage
kills_advantage = parser.get_kills_advantage_per_stage(hero_id)

print(f"\nKill Advantage: {kills_advantage}")
print(f"enemys: {enemy_ids}")
print(f"allies : {user_team_ids}")
print(f"counters_imp: {enemy_win_rates}")
print(f"synergy_imp: {ally_win_rates}")
print(f"meta_imp: {'пользователя' if team_advantage >= 0 else 'противников'} ({team_advantage:.2f})")

# user items per stage
player_items = parser.get_player_items(hero_id)

print("\nTarget items:")
for stage, items in player_items.items():
    print(f"{stage}: {items}")

# enemy items per stage
enemy_items = parser.get_filtered_enemy_items(hero_id)
print("\nОтфильтрованные предметы противников по этапам:")
for group, items in enemy_items.items():
    print(f"{group}: {items}")


print("\nenemy:")
for stage, items in enemy_items.items():
    print(f"{stage}: {items}")
