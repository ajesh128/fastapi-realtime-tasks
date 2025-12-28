from fastapi import FastAPI
from app.auth.routes import router as auth_router
from app.tasks.routes import router as task_router
from app.websockets.manager import ConnectionManager
from app.websockets.router import router as websocket_router

app = FastAPI()
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(task_router, prefix="/tasks", tags=["tasks"])

app.include_router(websocket_router, prefix="/websocket", tags=["websocket"])

