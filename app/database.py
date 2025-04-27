import asyncpg

from app.config import settings


class Database:
    pool: asyncpg.Pool = None

    @classmethod
    async def connect(cls):
        cls.pool = await asyncpg.create_pool(
            user=settings.DB_USER,
            password=settings.DB_PASS,
            database=settings.DB_NAME,
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            min_size=1,
            max_size=10,
        )

    @classmethod
    async def disconnect(cls):
        await cls.pool.close()

    @classmethod
    async def execute(
        cls,
        query: str,
        *args,
        fetch: bool = False,
        fetchval: bool = False,
        fetchrow: bool = False,
    ):
        async with cls.pool.acquire() as conn:
            if fetch:
                return await conn.fetch(query, *args)
            elif fetchval:
                return await conn.fetchval(query, *args)
            elif fetchrow:
                return await conn.fetchrow(query, *args)
            else:
                return await conn.execute(query, *args)
