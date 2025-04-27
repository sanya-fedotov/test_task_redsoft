import re
from typing import List, Optional

from pydantic import BaseModel, field_validator
from pydantic_settings import SettingsConfigDict

from app.emails.schemas import SEmail
from app.exceptions import (
    InvalidAgeFormatException,
    InvalidFullnameFormatException,
    InvalidPersonDataFormatException,
)


class SPersonOut(BaseModel):
    model_config = SettingsConfigDict(from_attributes=True)
    id: int
    name: str
    surname: str
    patronymic: Optional[str] = None
    age: Optional[int]
    gender: Optional[str]
    nationality: Optional[str]
    emails: List[SEmail] = []


class SPersonOutWithoutEmail(BaseModel):
    id: int
    name: str
    surname: str
    patronymic: Optional[str] = None
    age: Optional[int]
    gender: Optional[str]
    nationality: Optional[str]


class SPersonUpdate(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    patronymic: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None

    @field_validator("name", "surname", "patronymic", "nationality", "gender")
    def validate_alpha(cls, v):
        if v is not None and not re.fullmatch(r"[A-Za-z\- ]+", v):
            raise InvalidPersonDataFormatException
        return v

    @field_validator("age")
    def validate_age(cls, v):
        if v is not None and v < 0:
            raise InvalidAgeFormatException
        return v


class SPersonCreate(BaseModel):
    name: str
    surname: str
    patronymic: Optional[str] = None
    emails: Optional[List[SEmail]] = None

    @field_validator("name", "surname", "patronymic")
    def validate_alpha(cls, v):
        if v is not None and not re.fullmatch(r"[A-Za-z\- ]+", v):
            raise InvalidFullnameFormatException
        return v

    @field_validator("patronymic")
    @classmethod
    def validate_patronymic(cls, v):
        if v == "string" or not v:
            return None
        return v

    @field_validator("emails")
    @classmethod
    def validate_emails(cls, v):
        if not v:
            return None
        cleaned = [email for email in v if email.email != "user@example.com"]
        return cleaned or None  # если после очистки ничего нет, вернем None
