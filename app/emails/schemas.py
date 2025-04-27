from pydantic import BaseModel, EmailStr
from pydantic_settings import SettingsConfigDict


class SEmail(BaseModel):
    model_config = SettingsConfigDict(from_attributes=True)

    email: EmailStr
