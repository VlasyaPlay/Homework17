from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db
from typing import Annotated
from app.models.user import User
from app.models.task import Task
from app.schemas import CreateUser, UpdateUser
from sqlalchemy import insert, select, update, delete
from slugify import slugify


router = APIRouter(prefix='/user', tags=['user'])


@router.get('/')
async def all_users(db: Annotated[Session, Depends(get_db)]):
    users = db.scalars(select(User)).all()
    return users


@router.get('/user_id')
async def user_by_id(user_id: int, db: Annotated[Session, Depends(get_db)]):
    user = db.scalar(select(User).where(User.id == user_id))
    if user:
        return user
    raise HTTPException(status_code=404, detail='User was not found')


@router.post('/{user_id}/task')
async def task_by_user_id(user_id: int, db: Annotated[Session, Depends(get_db)]):
    user = db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User was not found")
    tasks = db.scalar(select(Task).where(Task.user_id == user_id)).all()
    return tasks


@router.post('/create')
async def create_user(create_new_user: CreateUser, db: Annotated[Session, Depends(get_db)]):

    db.execute(insert(User).values(username=create_new_user.username,
                                   firstname=create_new_user.firstname,
                                   lastname=create_new_user.lastname,
                                   age=create_new_user.age,
                                   slug=slugify(create_new_user.username)))
    db.commit()
    return {'status_code': status.HTTP_201_CREATED, 'transaction': 'Successful'}


@router.put('/update/')
async def update_user(user_update: UpdateUser, user_id: int, db: Annotated[Session, Depends(get_db)]):
    user = db.scalar(select(User).where(User.id == user_id))
    if user:
        db.execute(update(User).where(User.id == user_id).values(firstname=user_update.firstname,
                                                                 lastname=user_update.lastname,
                                                                 age=user_update.age))
        db.commit()
        return {'status_code': status.HTTP_200_OK, 'transaction': 'User update is successful!'}
    raise HTTPException(status_code=404, detail="User was not found")


@router.delete('/delete')
async def delete_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    user = db.scalar(select(User).where(User.id == user_id))
    if user:
        db.execute(delete(Task).where(Task.user_id == user_id))
        db.execute(delete(User).where(User.id == user_id))
        db.commit()
        return {'status_code': status.HTTP_200_OK, 'transaction': 'User deletion is successful!'}
    raise HTTPException(status_code=404, detail="User was not found")

