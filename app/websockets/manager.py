from fastapi import WebSocket
from typing import Dict

class ConnectionManager:
    def __init__(self):
        # user_id -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        self.active_connections.pop(user_id, None)

    async def send_to_user(self, user_id: str, message: str):
        websocket = self.active_connections.get(user_id)
        if websocket:
            await websocket.send_text(message)

manager = ConnectionManager()