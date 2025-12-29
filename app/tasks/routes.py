import logging
from fastapi import APIRouter, HTTPException, status, Depends,Path, BackgroundTasks

from app.celery_task.task import task_update
from app.core.dependencies import get_current_user, get_manager, is_admin_user
from app.tasks.schemas import TaskCreateModel, TaskUpdateModel
from app.tasks.service import TaskService

router = APIRouter()

@router.post("/create", status_code=201)
async def create_task(
    task_payload: TaskCreateModel,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_user),
):
    """
    API to create a new task for the logged-in user and trigger background processing.

    Args:
        task_payload (TaskCreateModel): Task data containing fields like:
            - title (str)
            - description (str)
            - due_date (optional, datetime)
        background_tasks (BackgroundTasks): FastAPI background task manager used to run async tasks.
        current_user (dict, optional): Logged-in user information injected by dependency. Defaults to Depends(get_current_user).

    Raises:
        HTTPException: 500 Internal Server Error if task creation or background processing fails.

    Returns:
        dict: JSON response containing:
            - message (str): Confirmation that the task was created.
            - task_id (str): ID of the newly created task.
            
        Example:
            {
                "message": "Task created successfully",
                "task_id": "694fb66fbd0312fac1d49c8b"
            }
    """
    try:
        # Create task
        task_id = await TaskService.create_task(
            task_payload.model_dump(),  
            current_user,
        )

        # Run async background processing
        background_tasks.add_task(
            TaskService.task_update,
            task_id,
            current_user.get("sub")
        )
        # Use celery if fast api background worker is not needed
        # task_id = str(task_id)
        # task_update.delay( task_id,
        #     current_user.get("sub"))

        return {
            "message": "Task created successfully",
            "task_id": str(task_id),
        }
    except HTTPException:   # Let HTTPExceptions propagate
        raise
    except Exception as exc:
        logging.error(f"Error in create_task: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred"
        ) from exc



@router.put("/update/{task_id}")
async def update_task(task_payload:TaskUpdateModel,task_id: str = Path(...),current_user=Depends(get_current_user)):
    """
    API to update an existing task for the logged-in user.

    Args:
        task_payload (TaskUpdateModel): _description_
        task_id (str, optional): _description_. Defaults to Path(...).
        current_user (_type_, optional): _description_. Defaults to Depends(get_current_user).

    Raises:
        HTTPException: 404 Not Found if the task does not exist.
        HTTPException: 403 Forbidden if the user is not authorized to update the task.
        HTTPException: 500 Internal Server Error for unexpected errors.

    Returns:
        dict: A success message and the updated task details.
    """
    try:
        await TaskService.parse_object_id(task_id)
        updated_task = await TaskService.update_task(task_payload.dict(),current_user,task_id)
        return {"message": "Task updated successfully", "task_details": updated_task}
    except HTTPException:   # Let HTTPExceptions propagate
        raise
    except Exception as exc:
        logging.error(f"Error in update_task: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred"
        ) from exc

@router.delete("/delete/{task_id}")
async def delete_task(task_id: str = Path(...),current_user=Depends(get_current_user)):
    """API to delete a task for the logged-in user.

    Args:
        task_id (str, optional): ID of the task to delete. Defaults to Path(...).
        current_user (dict, optional): Logged-in user information. Defaults to Depends(get_current_user).

    Raises:
        HTTPException: 404 Not Found if the task does not exist.
        HTTPException: 403 Forbidden if the user is not authorized to delete the task.
        HTTPException: 500 Internal Server Error for unexpected errors.

    Returns:
        _type_: _description_
    """
    try:
        await TaskService.parse_object_id(task_id)
        await TaskService.delete_task(task_id,current_user)
        return {"message": "Task deleted successfully"}
    except HTTPException:   # Let HTTPExceptions propagate
        raise
    except Exception as exc:
        logging.error(f"Error in delete_task: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred"
        ) from exc

@router.get("/user/tasks")
async def get_user_tasks(current_user=Depends(get_current_user)):
    """API to retrieve all tasks for the logged-in user.

    Args:
        current_user (dict, optional): Logged-in user information. Defaults to Depends(get_current_user).

    Raises:
        HTTPException: 404 Not Found if the user has no tasks.
        HTTPException: 500 Internal Server Error for unexpected errors.

    Returns:
        _type_: _description_
    """
    try:
        user_id = current_user.get("sub")
        tasks = await TaskService.get_tasks(user_id)
        # Convert ObjectId to string for each task
        for task in tasks:
            if "_id" in task:
                task["id"] = str(task["_id"])
                del task["_id"]
        return {"tasks": tasks}
    except HTTPException:   # Let HTTPExceptions propagate
        raise
    except Exception as exc:
        logging.error(f"Error in get_user_tasks: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred"
        ) from exc

### FOR ADMIN ONLY ###
@router.get("/all")
async def get_all_tasks():
    """API to retrieve all tasks in the system.

    Args:
        current_user (dict, optional): Logged-in user information. Defaults to Depends(get_current_user).
        _ (dict, optional): Admin user information. Defaults to Depends(is_admin_user).

    Raises:
        HTTPException: 403 Forbidden if the user is not authorized to access this resource.

    Returns:
        _type_: _description_
    """
    try:
        tasks = await TaskService.get_tasks()
        # Convert ObjectId to string for each task
        for task in tasks:
            if "_id" in task:
                task["id"] = str(task["_id"])
                del task["_id"]
        return {"tasks": tasks}
    except HTTPException:   # Let HTTPExceptions propagate
        raise
    except Exception as exc:
        logging.error(f"Error in get_all_tasks: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred"
        ) from exc


