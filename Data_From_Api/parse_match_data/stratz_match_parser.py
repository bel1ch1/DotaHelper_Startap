import json

# Загрузка JSON-файла
with open("match_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Основные данные матча
match_data = {
    "didRadiantWin": data["data"]["match"]["didRadiantWin"],
    "durationSeconds": data["data"]["match"]["durationSeconds"],
    "radiantKills": data["data"]["match"]["radiantKills"],
    "direKills": data["data"]["match"]["direKills"],
}


# Данные игроков
players_data = []
for player in data["data"]["match"]["players"]:
    player_info = {
        "isRadiant": player["isRadiant"],
        "heroId": player["heroId"],
        "heroShortName": player["hero"]["shortName"],
        "position": player["position"],
    }

    # События игрока
    playback_data = player["playbackData"]
    for event_type, events in playback_data.items():
        if events:  # Если есть события
            for event in events:
                event_data = {**player_info, "event_type": event_type, **event}
                players_data.append(event_data)

# Обработка inventoryEvents
inventory_events = []
for player in match_data.get("players", []):
    player_info = {
        "isRadiant": player.get("isRadiant"),
        "heroId": player.get("heroId"),
        "heroShortName": player.get("hero", {}).get("shortName"),
        "position": player.get("position"),
    }

    for event in player.get("playbackData", {}).get("inventoryEvents", []):
        event_data = {**player_info, "time": event.get("time")}

        # Обработка item0-item5
        for i in range(6):
            item_key = f"item{i}"
            item_data = event.get(item_key)
            event_data[item_key] = item_data.get("itemId") if item_data else None

        # Обработка backPack0-backPack2
        for i in range(3):
            backpack_key = f"backPack{i}"
            backpack_data = event.get(backpack_key)
            event_data[backpack_key] = backpack_data.get("itemId") if backpack_data else None

        # Обработка neutral0
        neutral_data = event.get("neutral0")
        event_data["neutral0"] = neutral_data.get("itemId") if neutral_data else None

        inventory_events.append(event_data)
        print(event_data)


spirit_bear_events = []
for player in match_data.get("players", []):
    player_info = {
        "isRadiant": player.get("isRadiant"),
        "heroId": player.get("heroId"),
        "heroShortName": player.get("hero", {}).get("shortName"),
        "position": player.get("position"),
    }

    for event in player.get("playbackData", {}).get("spiritBearInventoryEvents", []):
        event_data = {**player_info, "time": event.get("time")}

        # Обработка item0-item5
        for i in range(6):
            item_key = f"item{i}"
            item_data = event.get(item_key)
            event_data[item_key] = item_data.get("itemId") if item_data else None

        # Обработка backPack0-backPack2
        for i in range(3):
            backpack_key = f"backPack{i}"
            backpack_data = event.get(backpack_key)
            event_data[backpack_key] = backpack_data.get("itemId") if backpack_data else None

        # Обработка neutral0
        neutral_data = event.get("neutral0")
        event_data["neutral0"] = neutral_data.get("itemId") if neutral_data else None

        spirit_bear_events.append(event_data)


print(match_data)
print('============================================================================================')
print(players_data[0])
print(inventory_events)
