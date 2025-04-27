import asyncio
import asyncpg
from app.config import settings

CREATE_TABLES = """
CREATE TABLE IF NOT EXISTS people (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    surname TEXT NOT NULL,
    patronymic TEXT,
    age INTEGER,
    gender TEXT,
    nationality TEXT
);

CREATE TABLE IF NOT EXISTS emails (
    id SERIAL PRIMARY KEY,
    person_id INTEGER REFERENCES people(id) ON DELETE CASCADE,
    email TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS friendships (
    people_id INT NOT NULL,
    friend_id INT NOT NULL,
    PRIMARY KEY (people_id, friend_id),
    FOREIGN KEY (people_id) REFERENCES people(id) ON DELETE CASCADE,
    FOREIGN KEY (friend_id) REFERENCES people(id) ON DELETE CASCADE,
    CHECK (people_id <> friend_id)
);

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    person_id INTEGER NOT NULL UNIQUE
        REFERENCES people(id) ON DELETE CASCADE,
    email TEXT NOT NULL UNIQUE,
    hashed_password TEXT NOT NULL
);

"""

INSERT_SAMPLE_DATA = """
INSERT INTO people (name, surname, patronymic, age, gender, nationality)
VALUES ('John', 'Smith', 'Edwardovich', 30, 'male', 'US'),
    ('Anna', 'Petrova', 'Sergeevna', 28, 'female', 'RU'),
    ('James', 'Brown', NULL, 35, 'male', 'US'),
    ('Maria', 'Gonzalez', NULL, 22, 'female', 'ES'),
    ('Ahmed', 'Ali', NULL, 29, 'male', 'EG'),
    ('Liu', 'Wei', NULL, 31, 'male', 'CN'),
    ('Sarah', 'Connor', NULL, 27, 'female', 'US'),
    ('Omar', 'Hassan', NULL, 33, 'male', 'AE'),
    ('Yuki', 'Tanaka', NULL, 24, 'female', 'JP'),
    ('David', 'Johnson', NULL, 40, 'male', 'UK')
RETURNING id;
"""


INSERT_EMAILS = """
INSERT INTO emails (person_id, email)
VALUES ($1, 'ivan.ivanov@example.com'),
       ($1, 'ivan@example.com');
"""


async def seed():
    conn = await asyncpg.connect(
        user=settings.DB_USER,
        password=settings.DB_PASS,
        database=settings.DB_NAME,
        host=settings.DB_HOST,
        port=settings.DB_PORT,
    )
    try:
        await conn.execute(CREATE_TABLES)
        person_count = await conn.fetchval("SELECT COUNT(*) FROM people;")
        if person_count == 0:
            people_id = await conn.fetchval(INSERT_SAMPLE_DATA)
            await conn.execute(INSERT_EMAILS, people_id)
            print("База данных инициализирована")
        else:
            print("База данных уже содержит данные")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(seed())
