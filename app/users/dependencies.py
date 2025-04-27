from datetime import datetime, timezone

from fastapi import Depends, Request
from jose import JWTError, jwt

from app.config import settings
from app.database import Database
from app.exceptions import (
    IncorrectTokenFormatException,
    TokenAbsentException,
    TokenExpiredException,
    UserIsNotPresent,
)
from app.users.schemas import SUser


def get_token(request: Request):
    token = request.cookies.get("redsoft_access_token")
    if not token:
        raise TokenAbsentException
    return token


async def get_current_user(token: str = Depends(get_token)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, settings.ALGORITHM)
    except JWTError:
        raise IncorrectTokenFormatException

    exp = payload.get("exp")
    if not exp or int(exp) < datetime.now(timezone.utc).timestamp():
        raise TokenExpiredException

    user_id = payload.get("sub")
    if not user_id:
        raise UserIsNotPresent

    row = await Database.execute(
        "SELECT id, person_id, email FROM users WHERE id = $1",
        int(user_id),
        fetchrow=True,
    )
    if not row:
        raise UserIsNotPresent()

    # Преобразуем в Pydantic-модель
    return SUser(**dict(row))
