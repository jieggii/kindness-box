from tortoise import Tortoise


async def init(host: str, port: int, user: str, password: str, db: str):
    await Tortoise.init(
        {
            "connections": {
                "default": {
                    "engine": "tortoise.backends.asyncpg",
                    "credentials": {
                        "host": host,
                        "port": port,
                        "user": user,
                        "password": password,
                        "database": db,
                    },
                }
            },
            "apps": {"models": {"models": ["bot.db.models"], "default_connection": "default"}},
        }
    ),
    await Tortoise.generate_schemas()
