import json


# Загрузка JSON
path_to_data = 'match_data.json'
with open(path_to_data, 'r') as f:
    data = json.load(f)


#####################  Parser  ####################################################################
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


    def process_players(self):
        """
        Разделение игроков на команды Radiant и Dire.
        """
        # Создаем списки героев и сразу сортируем их по позициям
        self.radiant_heroes = sorted(
            [
                {"shortName": player["hero"]["shortName"], "heroId": player['heroId'], "position": player["position"]}
                for player in self.players
                if player.get("isRadiant", False)
            ],
            key=lambda x: self.position_order[x["position"]]
        )

        self.dire_heroes = sorted(
            [
                {"shortName": player["hero"]["shortName"], "heroId": player['heroId'], "position": player["position"]}
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
        if self.didRadiantWin is True:
            win = 'Radiant'
        else:
            win = 'Dire'
        return [win, self.durationSeconds]


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
###################################################################################################


parser = MatchParser(data)
parser.process_players()

# Пример использования
match_data = parser.get_match_data()
print("Match Data:", match_data)
print('===========================================')
radiant_heroes, dire_heroes = parser.get_sorted_heroes()
print("Radiant Heroes:", radiant_heroes)
print('===========================================')
print("Dire Heroes:", dire_heroes)
print('===========================================')
kills_advantage = parser.get_kills_advantage_per_minute(parser.radiantKills, parser.direKills)
print("Kills Advantage:", kills_advantage)
