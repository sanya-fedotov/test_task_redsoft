from fastapi import APIRouter, Body
from fastapi_versioning import version
from pydantic import EmailStr

from app.emails.dao import EmailsDAO

router = APIRouter(
    prefix="/emails",
    tags=["Эл. почта"]
)

@router.post("/{people_id}")
@version(1)
async def add_email(
    people_id: int,
    email: EmailStr = Body(..., embed=True),
):
    """
    Добавляет новый email пользователю по его ID.
    """
    return await EmailsDAO.add_email(people_id, email)
