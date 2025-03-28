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

        for p_id, data in self.hero_items.items():
            if data['isRadiant'] != player_team:  # Это противник
                enemy_ids.append(p_id)

        return enemy_ids


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



path_to_json = 'C:/work/DotaHelper_Startap/Data/not_dataset/match_data_v3.json'
with open(path_to_json, 'r') as f:
    new_data = json.load(f)


parser = NewMatchParser(new_data)

# Printing all heroes
parser.print_all_heroes()

hero_id = 82 #int(input("\nВведите ID героя пользователя: "))

winner = parser.get_winner()
print(f"\nПобедитель матча: {winner}")

result = parser.get_player_result(hero_id)
print(f"\nUser victory status: {result}")

kills_advantage = parser.get_kills_advantage_per_stage(hero_id)
print(f"\nKill Advantage (player perspective): {kills_advantage}")

stage_winners = parser.stage_winner(hero_id)
print(f"Stage Winners (player perspective): {stage_winners}")

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


# items_ids = {
#     0:"Blink Dagger",
#     1:"Blades of Attack",
#     2:"Helm of Iron Will",
#     3:"Javelin",
#     4:"Quelling Blade",
#     5:"Ring of Protection",
#     6:"Gauntlets of Strength",
#     7:"Slippers of Agility",
#     8:"Mantle of Intelligence",
#     9:"Iron Branch",
#     10:"Circlet",
#     11:"Gloves of Haste",
#     12:"Morbid Mask",
#     13:"Ring of Regen",
#     14:"Sage's Mask",
#     15:"Boots of Speed",
#     16:"Gem of True Sight",
#     17:"Cloak",
#     18:"Talisman of Evasion",
#     19:"Magic Stick",
#     20:"Magic Wand",
#     21:"Ghost Scepter",
#     22:"Clarity",
#     23:"Healing Salve",
#     24:"Dust of Appearance",
#     25:"Bottle",
#     26:"Tango",
#     27:"Boots of Travel",
#     28:"Phase Boots",
#     29:"Ring of Health",
#     30:"Power Treads",
#     31:"Hand of Midas",
#     32:"Bracer",
#     33:"Wraith Band",
#     34:"Null Talisman",
#     35:"Mekansm",
#     36:"Vladmir's Offering",
#     37:"Ring of Basilius",
#     38:"Pipe of Insight",
#     39:"Urn of Shadows",
#     40:"Headdress",
#     41:"Scythe of Vyse",
#     42:"Orchid Malevolence",
#     43:"Eul's Scepter of Divinity",
#     44:"Force Staff",
#     45:"Dagon",
#     46:"Aghanim's Scepter",
#     47:"Refresher Orb",
#     48:"Assault Cuirass",
#     49:"Heart of Tarrasque",
#     50:"Black King Bar",
#     51:"Shiva's Guard",
#     52:"Bloodstone",
#     53:"Linken's Sphere",
#     54:"Vanguard",
#     55:"Blade Mail",
#     56:"Divine Rapier",
#     57:"Monkey King Bar",
#     58:"Radiance",
#     59:"Butterfly",
#     60:"Daedalus",
#     61:"Skull Basher",
#     62:"Battle Fury",
#     63:"Manta Style",
#     64:"Crystalys",
#     65:"Armlet of Mordiggian",
#     66:"Shadow Blade",
#     67:"Sange and Yasha",
#     68:"Satanic",
#     69:"Mjollnir",
#     70:"Eye of Skadi",
#     71:"Sange",
#     72:"Helm of the Dominator",
#     73:"Maelstrom",
#     74:"Desolator",
#     75:"Yasha",
#     76:"Mask of Madness",
#     77:"Diffusal Blade",
#     78:"Ethereal Blade",
#     79:"Soul Ring",
#     80:"Arcane Boots",
#     81:"Orb of Venom",
#     82:"Drum of Endurance",
#     83:"Veil of Discord",
#     84:"Diffusal Blade (level 2)",
#     85:"Rod of Atos",
#     86:"Abyssal Blade",
#     87:"Heaven's Halberd",
#     88:"Tranquil Boots",
#     89:"Enchanted Mango",
#     90:"Boots of Travel 2",
#     91:"Meteor Hammer",
#     92:"Nullifier",
#     93:"Lotus Orb",
#     94:"Solar Crest",
#     95:"Guardian Greaves",
#     96:"Aether Lens",
#     97:"Octarine Core",
#     98:"Dragon Lance",
#     99:"Faerie Fire",
#     100:"Crimson Guard",
#     101:"Wind Lace",
#     102:"Moon Shard",
#     103:"Silver Edge",
#     104:"Bloodthorn",
#     105:"Echo Sabre",
#     106:"Glimmer Cape",
#     107:"Aeon Disk",
#     108:"Kaya",
#     109:"Crown",
#     110:"Hurricane Pike",
#     111:"Infused Raindrops",
#     112:"Spirit Vessel",
#     113:"Holy Locket",
#     114:"Kaya and Sange",
#     115:"Yasha and Kaya",
#     116:"Voodoo Mask",
#     117:"Witch Blade",
#     118:"Falcon Blade",
#     119:"Mage Slayer",
#     120:"Overwhelming Blink",
#     121:"Swift Blink",
#     123:"Arcane Blink",
#     124:"Aghanim's Shard",
#     125:"Wind Waker",
#     126:"Helm of the Overlord",
#     127:"Eternal Shroud",
#     128:"Revenant's Brooch",
#     129:"Boots of Bearing",
#     130:"Harpoon",
#     131:"Diffusal Blade",
#     132:"Disperser",
#     133:"Phylactery",
#     134:"Blood Grenade",
#     135:"Pavise",
#     136:"Gleipnir",
#     137:"Orb of Frost",
#     138:"Parasma",
#     139:"Khanda"
# }
