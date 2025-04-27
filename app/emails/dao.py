from pydantic import EmailStr

from app.database import Database
from app.exceptions import EmailAlreadyExistsException, NotFindPersonException


class EmailsDAO:
    @staticmethod
    async def add_email(people_id: int, email: EmailStr):
        people = await Database.execute(
            "SELECT 1 FROM people WHERE id = $1",
            people_id,
            fetchval=True
        )
        if not people:
            raise NotFindPersonException

        existing_email = await Database.execute(
            "SELECT 1 FROM emails WHERE email = $1",
            email,
            fetchval=True
        )
        if existing_email:
            raise EmailAlreadyExistsException

        await Database.execute(
            "INSERT INTO emails (person_id, email) VALUES ($1, $2)",
            people_id,
            email
        )

        return {"people_id": people_id, "email": email}
