import re
from typing import List

from fastapi import APIRouter, Body, Path, Query
from fastapi_cache.decorator import cache
from fastapi_versioning import version

from app.exceptions import (
    EmptyDatabaseException,
    InvalidSurnameFormatException,
    MissingNameOrSurnameException,
    NotFindPersonException,
    NotFindSurnameException,
)
from app.people import schemas
from app.people.dao import PeopleDAO

router = APIRouter(
    prefix="/People",
    tags=["Пользователи"],
)


@router.get("/get_all")
@version(1)
async def get_all_people() -> List[schemas.SPersonOut]:
    """
    Выводит список всех пользователей
    """
    result = await PeopleDAO.get_all()
    if not result:
        raise EmptyDatabaseException
    return result


@router.get("/find_by_surname")
@version(1)
async def find_by_surname(surname: str = Query(...)) -> List[schemas.SPersonOut]:
    """
    Выводит всю по фамилии сводную информацию
    """

    # Проверяем правильности фамилии
    if not re.fullmatch(r"[A-Za-z]+", surname):
        raise InvalidSurnameFormatException
    result = await PeopleDAO.find_by_surname(surname)

    # Проверяем наличие пользователя
    if not result:
        raise NotFindSurnameException
    return result


@router.patch("/{people_id}")
@version(1)
async def update_person_by_id(
    people_id: int = Path(...), payload: schemas.SPersonUpdate = Body(...)
) -> schemas.SPersonOutWithoutEmail:
    """
    Изменяет информацию о пользователе
    """
    updated = await PeopleDAO.update_person(
        people_id, payload.model_dump(exclude_unset=True)
    )
    if not updated:
        raise NotFindPersonException
    return updated


@router.post("/")
@version(1)
async def add_person(payload: schemas.SPersonCreate = Body(...)) -> schemas.SPersonOut:
    if payload.name == "string" or payload.surname == "string":
        raise MissingNameOrSurnameException
    """
    Принимает информацию о новом человеке и создает запись в БД
    """
    return await PeopleDAO.add_person(payload.model_dump())


# ДАЛЬШЕ РОУТЕРЫ VERSION 2

router_with_cache = APIRouter(
    tags=["Кеширование"],
)


@router_with_cache.get("/get_all")
@cache(expire=10)
@version(2)
async def get_all_people_with_cache() -> List[schemas.SPersonOut]:
    """
    Выводит список всех пользователей
    """
    result = await PeopleDAO.get_all_with_delay()
    if not result:
        raise EmptyDatabaseException
    return result


@router_with_cache.get("/find_by_surname")
@cache(expire=10)
@version(2)
async def find_by_surname_with_cache(
    surname: str = Query(...),
) -> List[schemas.SPersonOut]:
    """
    Выводит всю по фамилии сводную информацию
    """

    # Проверяем правильности фамилии
    if not re.fullmatch(r"[A-Za-z]+", surname):
        raise InvalidSurnameFormatException
    result = await PeopleDAO.find_by_surname_with_delay(surname)

    # Проверяем наличие пользователя
    if not result:
        raise NotFindSurnameException
    return result
