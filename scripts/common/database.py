import asyncio

from bot.database.init import init_database as _init_database
# from bot.__main__ import read_file

from loguru import logger

MONGO_USERNAME_FILE = "./.secrets/mongo/username"
MONGO_PASSWORD_FILE = "./.secrets/mongo/password"


def read_file(filepath: str) -> str:
    with open(filepath, "r") as file:
        return file.read().strip()


def init_database(loop: asyncio.AbstractEventLoop, host: str, port: int, database: str) -> None:
    logger.info("reading mongo credentials")
    username, password = read_file(MONGO_USERNAME_FILE), read_file(MONGO_PASSWORD_FILE)

    logger.info(f"connecting to mongo database {database} at {username}@{host}:{port}")

    loop.run_until_complete(
        _init_database(host=host, port=port, username=username, password=password, database=database)
    )
