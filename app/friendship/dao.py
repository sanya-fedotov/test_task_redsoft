import json

from app.database import Database
from app.exceptions import (
    AlreadyFriendsException,
    CannotAddYourselfException,
    NotFindPeopleException,
    NotFindPersonException,
)
from app.people.schemas import SPersonOut


class FriendsDAO:

    @staticmethod
    async def add_friend(people_id: int, friend_id: int):
        if people_id == friend_id:
            raise CannotAddYourselfException

        people_check = await Database.execute(
            "SELECT id FROM people WHERE id = ANY($1::int[])",
            [people_id, friend_id],
            fetch=True,
        )
        if len(people_check) < 2:
            raise NotFindPeopleException

        existing = await Database.execute(
            "SELECT 1 FROM friendships WHERE people_id = $1 AND friend_id = $2",
            people_id,
            friend_id,
            fetchval=True,
        )
        if existing:
            raise AlreadyFriendsException

        query = """
            INSERT INTO friendships (people_id, friend_id) VALUES ($1, $2)
            ON CONFLICT DO NOTHING
        """
        await Database.execute(query, people_id, friend_id)
        await Database.execute(query, friend_id, people_id)  

    @staticmethod
    async def get_friends(people_id: int):
        person_exists = await Database.execute(
            "SELECT 1 FROM people WHERE id = $1", people_id, fetchval=True
        )
        if not person_exists:
            raise NotFindPersonException

        query = """
            SELECT p.id, p.name, p.surname, p.patronymic, p.age, p.gender, p.nationality,
                COALESCE(json_agg(json_build_object('email', e.email)) FILTER (WHERE e.email IS NOT NULL), '[]') AS emails
            FROM friendships f
            JOIN people p ON p.id = f.friend_id
            LEFT JOIN emails e ON p.id = e.person_id
            WHERE f.people_id = $1
            GROUP BY p.id
        """
        rows = await Database.execute(query, people_id, fetch=True)
        return [
            SPersonOut(**{**dict(row), "emails": json.loads(row["emails"])})
            for row in rows
        ]
