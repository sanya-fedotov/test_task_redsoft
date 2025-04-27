from typing import List

from fastapi import APIRouter
from fastapi_versioning import version

from app.friendship.dao import FriendsDAO
from app.people import schemas

router = APIRouter(
    prefix="/Friend",
    tags=["Друзья"],
)


@router.post("/{people_id}/friends/{friend_id}")
@version(1)
async def add_friend(people_id: int, friend_id: int):
    """
    Добавляет дружбу между двумя пользователями
    """
    await FriendsDAO.add_friend(people_id, friend_id)
    return {"message": "Друзья успешно добавлены"}


@router.get("/{people_id}/friends")
async def get_friends(people_id: int) -> List[schemas.SPersonOut]:
    """
    Возвращает список друзей пользователя
    """
    return await FriendsDAO.get_friends(people_id)
