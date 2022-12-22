from tortoise import Tortoise

from app.config import config


async def init():
    await Tortoise.init(
        {
            "connections": {
                "default": {
                    "engine": "tortoise.backends.asyncpg",
                    "credentials": {
                        "host": config.PG.HOST,
                        "port": config.PG.PORT,
                        "user": config.PG.USER,
                        "password": config.PG.PASSWORD,
                        "database": config.PG.DATABASE,
                    },
                }
            },
            "apps": {"models": {"models": ["app.db.models"], "default_connection": "default"}},
        }
    ),
    await Tortoise.generate_schemas()
