import asyncio
import sys

import uvloop
from loguru import logger
from vkwave.bots import SimpleLongPollBot
from vkwave.bots.core.dispatching import filters

from bot.database.init import init_database
from bot.env import env
from bot.routers import home, registration


def read_file(filepath: str) -> str:
    with open(filepath, "r") as file:
        return file.read().strip()


# install uvloop:
uvloop.install()
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# initialize database:
loop.run_until_complete(
    init_database(
        host=env.Mongo.HOST,
        port=env.Mongo.PORT,
        username=read_file(env.Mongo.USERNAME_FILE),
        password=read_file(env.Mongo.PASSWORD_FILE),
        database=env.Mongo.DATABASE,
    ),
)

# initialize bot:
access_token = read_file(env.Bot.ACCESS_TOKEN_FILE)
group_id = int(read_file(env.Bot.GROUP_ID_FILE))

bot = SimpleLongPollBot(tokens=[access_token], group_id=group_id)
bot.router.registrar.add_default_filter(filters.EventTypeFilter("message_new"))

bot.dispatcher.add_router(registration.router)
bot.dispatcher.add_router(home.router)

try:
    logger.info("starting bot")
    bot.run_forever(ignore_errors=True)

except KeyboardInterrupt:
    sys.exit()
