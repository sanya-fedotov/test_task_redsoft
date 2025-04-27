from fastapi import APIRouter, Depends, Response
from fastapi_versioning import version

from app.exceptions import MissingNameOrSurnameException, UserAlreadyExistsException
from app.people.dao import PeopleDAO
from app.people.schemas import SPersonOut
from app.users.auth import authenticate_user, create_access_token, get_password_hash
from app.users.dao import UsersDAO
from app.users.dependencies import get_current_user
from app.users.schemas import SUser, SUserLogin, SUserOut, SUserRegister

router = APIRouter(prefix="/auth", tags=["Авторизация и Аутентификация"])


@router.post("/register")
@version(2)
async def register(user: SUserRegister) -> SUserOut:
    existing = await UsersDAO.find_by_email(user.email)
    if existing:
        raise UserAlreadyExistsException
    if user.name == "string" or user.surname == "string":
        raise MissingNameOrSurnameException
    created = await UsersDAO.register(user)
    return SUserOut(**created)


@router.post("/login")
@version(2)
async def login_user(response: Response, credentials: SUserLogin):
    user = await authenticate_user(credentials.email, credentials.password)
    access_token = create_access_token({"sub": str(user["id"])})
    response.set_cookie("redsoft_access_token", access_token, httponly=True)
    return {"access_token": access_token}


@router.post("/logout")
@version(2)
async def logout_user(responce: Response):
    responce.delete_cookie("redsoft_access_token")
    return {"message": "Logged out"}


@router.get("/me")
@version(2)
async def read_users_me(current_user: SUser = Depends(get_current_user)) -> SPersonOut:
    """
    Возвращает информацию о связанном с токеном человеке
    """
    return await PeopleDAO.get_by_id(current_user.person_id)
