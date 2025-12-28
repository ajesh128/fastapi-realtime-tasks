from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from app.core.dependencies import get_manager
from app.websockets import manager
from app.websockets.manager import manager

router = APIRouter()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(user_id, websocket)
    try:
        while True:
            # Keeps the connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)
