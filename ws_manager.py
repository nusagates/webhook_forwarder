from typing import Dict, List
from fastapi import WebSocket
import json

class ConnectionManager:
    def __init__(self):
        # Maps endpoint_id to a list of active websocket connections
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, endpoint_id: int):
        await websocket.accept()
        if endpoint_id not in self.active_connections:
            self.active_connections[endpoint_id] = []
        self.active_connections[endpoint_id].append(websocket)

    def disconnect(self, websocket: WebSocket, endpoint_id: int):
        if endpoint_id in self.active_connections:
            if websocket in self.active_connections[endpoint_id]:
                self.active_connections[endpoint_id].remove(websocket)
            if not self.active_connections[endpoint_id]:
                del self.active_connections[endpoint_id]

    async def broadcast_to_endpoint(self, endpoint_id: int, message: dict):
        if endpoint_id in self.active_connections:
            for connection in self.active_connections[endpoint_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    pass

manager = ConnectionManager()
