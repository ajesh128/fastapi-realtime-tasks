import asyncio
import logging

from app.database.asyncdb.models import Tasks
from app.tasks.service import TaskService
from app.websockets.manager import manager
from app.worker.celer_worker import celery_app
from bson import ObjectId

@celery_app.task(name="app.celery_task.task.task_update")
def task_update(task_id,user_id):
    task_id = ObjectId(task_id)
    asyncio.run(TaskService.task_update(task_id,user_id))
    