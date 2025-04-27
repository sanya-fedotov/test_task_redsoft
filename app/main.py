from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware import Middleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from fastapi_versioning import VersionedFastAPI, version
from prometheus_fastapi_instrumentator import Instrumentator
from redis import asyncio as aioredis
from starlette.middleware.sessions import SessionMiddleware

from app.database import Database
from app.emails.router import router as router_emails
from app.friendship.router import router as router_friends
from app.people.router import router as router_people
from app.people.router import router_with_cache
from app.prometheus.router import router as router_prometheus
from app.users.router import router as router_auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    # === startup ===
    # 1) Подключаемся к БД
    await Database.connect()

    # 2) Настраиваем редис и FastAPICache
    #    если у вас в docker-compose сервис назван "redis",
    #    то URL будет "redis://redis:6379/0"
    redis = aioredis.from_url(
        "redis://localhost:6379", 
        encoding="utf8", 
        decode_responses=True
    )
    FastAPICache.init(RedisBackend(redis), prefix="cache")

    yield
    # === shutdown ===
    await Database.disconnect()


orig_app = FastAPI(
    lifespan=lifespan,
    middleware=[Middleware(SessionMiddleware, secret_key="mysecretkey")],
)
orig_app.include_router(router_people)
orig_app.include_router(router_emails)
orig_app.include_router(router_friends)
orig_app.include_router(router_with_cache)
orig_app.include_router(router_auth)
orig_app.include_router(router_prometheus)

# А теперь версионируем — при этом передаём туда тот же lifespan!
app = VersionedFastAPI(
    orig_app,
    version_format="{major}",
    prefix_format="/v{major}",
    description="Greet users with a nice message",
    # ↓ этот lifespan прокинется в новый FastAPI
    lifespan=lifespan,
)

instrumentator = Instrumentator(
    should_group_status_codes=False,
    excluded_handlers=["/metrics"],
)

instrumentator.instrument(app).expose(app)
