import re
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator

from app.exceptions import InvalidFullnameFormatException


class SUser(BaseModel):
    id: int
    person_id: int
    email: EmailStr


class SUserRegister(BaseModel):
    name: str
    surname: str
    patronymic: Optional[str] = None
    email: EmailStr
    password: str

    @field_validator("name", "surname", "patronymic")
    def alpha_only(cls, v):
        if v is not None and not re.fullmatch(r"[A-Za-z\- ]+", v):
            raise InvalidFullnameFormatException
        return v


class SUserLogin(BaseModel):
    email: EmailStr
    password: str


class SUserOut(BaseModel):
    id: int
    email: EmailStr
    person_id: int
    name: str
    surname: str
    patronymic: Optional[str] = None
    age: Optional[int]
    gender: Optional[str]
    nationality: Optional[str]
