import asyncio
import websockets
import json
from datetime import datetime

# Ваши данные (замените на реальный источник)
def get_current_data():
    return [
        f"Обновлено: {datetime.now().strftime('%H:%M:%S')}",
        "Статус: Активно",
        "Игроков онлайн: 42",
        "Событие: Турнир",
        "След. матч через: 15 мин"
    ]

# WebSocket сервер
async def server(websocket, path):
    while True:
        try:
            data = get_current_data()
            await websocket.send(json.dumps(data))
            await asyncio.sleep(1)  # Обновление каждую секунду
        except websockets.exceptions.ConnectionClosed:
            break

start_server = websockets.serve(server, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
