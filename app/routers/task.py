from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db
from typing import Annotated
from app.models.task import Task
from app.models.user import User
from app.schemas import CreateTask, UpdateTask, CreateUser
from sqlalchemy import insert, select, update, delete
from slugify import slugify

router = APIRouter(prefix='/task', tags=['task'])


@router.get('/')
async def all_tasks(db: Annotated[Session, Depends(get_db)]):
    tasks = db.scalars(select(Task)).all()
    return tasks


@router.get('/task_id')
async def task_by_id(task_id: int, db: Annotated[Session, Depends(get_db)]):
    task = db.scalar(select(Task).where(Task.id == task_id))
    if task:
        return task
    raise HTTPException(status_code=404, detail='User was not found')


@router.post('/create')
async def create_task(create_new_task: CreateTask, user_id: int, db: Annotated[Session, Depends(get_db)]):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User was not found")

    db.execute(insert(Task).values(title=create_new_task.title,
                                   content=create_new_task.content,
                                   priority=create_new_task.priority,
                                   slug=slugify(create_new_task.title),
                                   user_id=user.id))
    db.commit()
    return {'status_code': status.HTTP_201_CREATED, 'transaction': 'Successful'}


@router.put('/update')
async def update_task(task_update: UpdateTask, task_id: int, db: Annotated[Session, Depends(get_db)]):
    task = db.scalar(select(Task).where(Task.id == task_id))
    if task:
        db.execute(update(Task).where(Task.id == task_id).values(title=task_update.title,
                                                                 content=task_update.content,
                                                                 priority=task_update.priority ))
        db.commit()
        return {'status_code': status.HTTP_200_OK, 'transaction': 'User update is successful!'}
    raise HTTPException(status_code=404, detail="User was not found")


@router.delete('/delete')
async def delete_task(task_id: int, db: Annotated[Session, Depends(get_db)]):
    task = db.scalar(select(Task).where(Task.id == task_id))
    if task:
        db.execute(delete(Task).where(Task.id == task_id).execution_options(synchronize_session=False))
        db.commit()
        return {'status_code': status.HTTP_200_OK, 'transaction': 'Task deletion is successful!'}
    raise HTTPException(status_code=404, detail="User was not found")

