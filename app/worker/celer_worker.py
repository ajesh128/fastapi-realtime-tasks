from celery import Celery
from app.core.config import Config

celery_app = Celery(
    "test_worker",
    broker=Config.BROKER_URL,
    backend=Config.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_routes={
        "app.celery_task.task.task_update": {"queue": "default_queue"},
    }
)

celery_app.conf.imports = ["app.celery_task.task"]
