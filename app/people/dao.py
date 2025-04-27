import asyncio
import json

from app.database import Database
from app.exceptions import EmailAlreadyExistsException, NotFindPersonException
from app.people.external_API.connection import fetch_person_data
from app.people.schemas import SPersonOut, SPersonOutWithoutEmail


class PeopleDAO:

    @staticmethod
    async def get_all():
        query = """
            SELECT 
                p.id, p.name, p.surname, p.patronymic, p.age, p.gender, p.nationality,
                COALESCE(json_agg(json_build_object('email', e.email)) FILTER (WHERE e.email IS NOT NULL), '[]') AS emails
            FROM people p
            LEFT JOIN emails e ON p.id = e.person_id
            GROUP BY p.id
        """
        rows = await Database.execute(query, fetch=True)
        return [
            SPersonOut(**{**dict(row), "emails": json.loads(row["emails"])})
            for row in rows
        ]

    @staticmethod
    async def find_by_surname(surname: str):
        query = """
            SELECT 
                p.id, p.name, p.surname, p.patronymic, p.age, p.gender, p.nationality,
                COALESCE(json_agg(json_build_object('email', e.email)) FILTER (WHERE e.email IS NOT NULL), '[]') AS emails
            FROM people p
            LEFT JOIN emails e ON p.id = e.person_id
            WHERE p.surname ILIKE $1
            GROUP BY p.id
        """
        rows = await Database.execute(query, surname, fetch=True)
        return [
            SPersonOut(**{**dict(row), "emails": json.loads(row["emails"])})
            for row in rows
        ]

    @staticmethod
    async def update_person(people_id: int, data: dict):
        # Проверка существования человека
        person_exists = await Database.execute(
            "SELECT 1 FROM people WHERE id = $1", people_id, fetchval=True
        )
        if not person_exists:
            raise NotFindPersonException

        # Обновление полей
        fields, values = [], []
        index = 1
        for key in ["name", "surname", "patronymic", "age", "gender", "nationality"]:
            if key in data and data[key] not in ["string", 0, ["string"]]:
                fields.append(f"{key} = ${index}")
                values.append(data[key])
                index += 1

        if fields:
            query = f"UPDATE people SET {', '.join(fields)} WHERE id = ${index}"
            values.append(people_id)
            await Database.execute(query, *values)

        # Получение обновлённого пользователя
        row = await Database.execute(
            """
            SELECT id, name, surname, patronymic, age, gender, nationality
            FROM people
            WHERE id = $1
            """,
            people_id,
            fetchrow=True,
        )

        return SPersonOutWithoutEmail(**dict(row))

    @staticmethod
    async def add_person(data: dict):
        external = await fetch_person_data(data["name"])

        async with Database.pool.acquire() as conn:
            async with conn.transaction():
                # Вставка нового человека
                people_id = await conn.fetchval(
                    """
                    INSERT INTO people (name, surname, patronymic, age, gender, nationality)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    RETURNING id
                    """,
                    data["name"],
                    data["surname"],
                    data.get("patronymic"),
                    external["age"],
                    external["gender"],
                    external["nationality"],
                )

                # Вставка email'ов
                if data.get("emails"):
                    for email in data["emails"]:
                        existing_email = await conn.fetchval(
                            "SELECT 1 FROM emails WHERE email = $1",
                            email["email"],
                        )
                        if existing_email:
                            raise EmailAlreadyExistsException

                        await conn.execute(
                            "INSERT INTO emails (person_id, email) VALUES ($1, $2)",
                            people_id,
                            email["email"],
                        )

        # Получаем полную информацию о человеке с email'ами
        row = await Database.execute(
            """
            SELECT p.id, p.name, p.surname, p.patronymic, p.age, p.gender, p.nationality,
                COALESCE(json_agg(json_build_object('email', e.email)) 
                            FILTER (WHERE e.id IS NOT NULL), '[]') AS emails
            FROM people p
            LEFT JOIN emails e ON p.id = e.person_id
            WHERE p.id = $1
            GROUP BY p.id
            """,
            people_id,
            fetchrow=True,
        )

        # Возвращаем сериализованный ответ
        return SPersonOut(**{**dict(row), "emails": json.loads(row["emails"])})

    # ДАЛЬШЕ ЗАПРОСЫ VERSION 2

    @staticmethod
    async def get_all_with_delay():
        query = """
            SELECT 
                p.id, p.name, p.surname, p.patronymic, p.age, p.gender, p.nationality,
                COALESCE(json_agg(json_build_object('email', e.email)) FILTER (WHERE e.email IS NOT NULL), '[]') AS emails
            FROM people p
            LEFT JOIN emails e ON p.id = e.person_id
            GROUP BY p.id
        """
        rows = await Database.execute(query, fetch=True)
        await asyncio.sleep(3)
        return [
            SPersonOut(**{**dict(row), "emails": json.loads(row["emails"])})
            for row in rows
        ]

    @staticmethod
    async def find_by_surname_with_delay(surname: str):
        query = """
            SELECT 
                p.id, p.name, p.surname, p.patronymic, p.age, p.gender, p.nationality,
                COALESCE(json_agg(json_build_object('email', e.email)) FILTER (WHERE e.email IS NOT NULL), '[]') AS emails
            FROM people p
            LEFT JOIN emails e ON p.id = e.person_id
            WHERE p.surname ILIKE $1
            GROUP BY p.id
        """
        rows = await Database.execute(query, surname, fetch=True)
        await asyncio.sleep(3)
        return [
            SPersonOut(**{**dict(row), "emails": json.loads(row["emails"])})
            for row in rows
        ]

    @staticmethod
    async def get_by_id(person_id: int) -> SPersonOut:
        row = await Database.execute(
            """
            SELECT p.id, p.name, p.surname, p.patronymic, p.age, p.gender, p.nationality,
                   COALESCE(
                     json_agg(json_build_object('email', e.email))
                     FILTER (WHERE e.email IS NOT NULL), '[]'
                   ) AS emails
            FROM people p
            LEFT JOIN emails e ON p.id = e.person_id
            WHERE p.id = $1
            GROUP BY p.id
            """,
            person_id,
            fetchrow=True,
        )
        return SPersonOut(**{**dict(row), "emails": json.loads(row["emails"])})
