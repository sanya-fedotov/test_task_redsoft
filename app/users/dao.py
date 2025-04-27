from asyncpg import UniqueViolationError
from passlib.context import CryptContext

from app.database import Database
from app.people.external_API.connection import fetch_person_data
from app.users.schemas import SUserRegister

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UsersDAO:

    @staticmethod
    async def register(user: SUserRegister):
        hashed = pwd_context.hash(user.password)
        external = await fetch_person_data(user.name)
        async with Database.pool.acquire() as conn:
            async with conn.transaction():
                # 1) вставляем в people
                person_id = await conn.fetchval(
                    """
                    INSERT INTO people (name, surname, patronymic, age, gender, nationality)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    RETURNING id
                    """,
                    user.name,
                    user.surname,
                    user.patronymic,
                    external["age"],
                    external["gender"],
                    external["nationality"],
                )

                # 2) вставляем в users
                try:
                    await conn.execute(
                        """
                        INSERT INTO users (person_id, email, hashed_password)
                        VALUES ($1, $2, $3)
                        """,
                        person_id,
                        user.email,
                        hashed,
                    )
                except UniqueViolationError:
                    raise

                # 3) вставляем в emails
                await conn.execute(
                    """
                    INSERT INTO emails (person_id, email)
                    VALUES ($1, $2)
                    """,
                    person_id,
                    user.email,
                )
        row = await Database.execute(
            """
            SELECT u.id, u.email, u.person_id,
                   p.name, p.surname, p.patronymic, p.age, p.gender, p.nationality
            FROM users u
            JOIN people p ON p.id = u.person_id
            WHERE u.person_id = $1
            """,
            person_id,
            fetchrow=True,
        )
        return dict(row)

    @staticmethod
    async def find_by_email(email: str):
        return await Database.execute(
            """
            SELECT u.id, u.email, u.hashed_password, u.person_id,
                   p.name, p.surname, p.patronymic, p.age, p.gender, p.nationality
            FROM users u
            JOIN people p ON p.id = u.person_id
            WHERE u.email = $1
            """,
            email,
            fetchrow=True,
        )

    @staticmethod
    async def find_by_id(uid: int):
        row = await Database.execute(
            """
            SELECT u.id, u.email, u.person_id,
                   p.name, p.surname, p.patronymic, p.age, p.gender, p.nationality
            FROM users u
            JOIN people p ON p.id = u.person_id
            WHERE u.id = $1
            """,
            uid,
            fetchrow=True,
        )
        return row
