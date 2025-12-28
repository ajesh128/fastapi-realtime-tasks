import logging
from fastapi import Depends, HTTPException,status,BackgroundTasks
from app.database.asyncdb.models import Users,Tasks
from datetime import datetime, timezone
from bson import ObjectId
import asyncio

from app.websockets.manager import manager



class TaskService:
    @staticmethod
    async def create_task(task_data: dict, user: dict) -> str:
        try:
            existing_task = await TaskService.has_task(task_data.get("title"), user.get("sub"))
            if existing_task:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Task already exists"
                )
            user_id = user.get("sub")
            task_data.update({"user_id": user_id,"created_at": str(datetime.now(timezone.utc))})
            doc_id =await Tasks().insert_one({**task_data})
            task_id = doc_id.inserted_id
            return task_id
        except HTTPException as exc:
            raise
        except Exception as exc:
            logging.error(f'error occured in create task function {exc}')
            return {}
    @staticmethod
    async def update_task(task_data: dict, user:str,task_id:str) -> dict:
        try:
            user_id = user.get("sub")
            existing_task = await TaskService.has_task(task_data.get("title"), user_id,task_id)
            if not existing_task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Task not found"
                )
            
            updated_details = await Tasks().find_one_and_update(
                {"_id": ObjectId(task_id)},
                {"$set": task_data}
            )
            return updated_details
        except HTTPException:   # Let HTTPExceptions propagate
            raise
        except Exception as exc:
            logging.error(f'error occured in update task function {exc}')
            return {}

    @staticmethod
    async def has_task(title: str, user_id: str,task_id: str="") -> str:
        try:
            query_dict = {}
            if task_id:
                query_dict.update({"_id":ObjectId(task_id)})
            else:
                query_dict.update({"title": title, "user_id": user_id})
            task = await Tasks().find(query_dict)
            return task
        except Exception as exc:
            logging.error(f'error occured in has task function')
            return ""
    
    @staticmethod
    async def parse_object_id(id_str: str):
        try:
            if ObjectId.is_valid(id_str):
                return ObjectId(id_str)
            raise HTTPException(status_code=400, detail="Invalid ObjectId")
        except HTTPException:   # Let HTTPExceptions propagate
            raise
        except Exception as exc:
            logging.error(f'error occured in parse_object_id function {exc} ')
    
    @staticmethod
    async def delete_task(task_id: str, current_user: dict) ->bool:
        has_task = await Tasks().find_one({"_id": ObjectId(task_id), "user_id": current_user.get("sub")})
        try:
            if not has_task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Task not found"
                )
            await Tasks().delete_one({"_id": ObjectId(task_id)})
            return True
        except HTTPException:   # Let HTTPExceptions propagate
            raise
        except Exception as exc:
            logging.error(f'error occured in delete task function {exc}')
            return False
    
    @staticmethod
    async def get_tasks(user_id: str | None = None) ->list:
        try:
            query = {"user_id": user_id} if user_id else {}
            tasks = await Tasks().find(query)
            if not tasks:
                return []

            return tasks
        except Exception as exc:
            logging.error(f'error occured in get task function {exc}')
            return []

    
    @staticmethod
    async def task_update(task_id,user_id):
        """
        TO UPDATE TASK

        Args:
            task_id (_type_): _description_
            user_id (_type_): _description_
        """
        await asyncio.sleep(10)
        await Tasks().update_one({"_id":task_id},{"$set":{"status":"completed"}})
        await manager.send_to_user(
        user_id,
        f"Task {task_id} completed"
    )


