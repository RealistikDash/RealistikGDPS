from __future__ import annotations

import httpx
from databases import DatabaseURL
from redis import asyncio as aioredis

from realistikgdps.config import config
from realistikgdps.services.mysql import MySQLService

http = httpx.AsyncClient()
database = MySQLService(
    DatabaseURL(
        "mysql+asyncmy://{username}:{password}@{host}:{port}/{db}".format(
            username=config.sql_user,
            password=config.sql_pass,
            host=config.sql_host,
            port=config.sql_port,
            db=config.sql_db,
        ),
    ),
)
redis = aioredis.from_url(
    f"redis://{config.redis_host}:{config.redis_port}/{config.redis_db}",
)
