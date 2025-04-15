from typing import List
from fastapi import WebSocket


class WebSocketManager:
    def __init__(self):

        # список активных соединений
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()  # принимаем соединение
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        # рассылаем сообщение всем подключенным клиентам
        for connection in self.active_connections:
            await connection.send_text(message)
