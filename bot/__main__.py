import asyncio
import logging
import sys

import uvloop
from bot import db
from bot.env import env
from bot.routers import home, registration
from bot.util import read_file
from vkwave.bots import SimpleLongPollBot
from vkwave.bots.core.dispatching import filters

logging.basicConfig(level=logging.INFO)

uvloop.install()

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(db.init(
    host=env.Postgres.HOST,
    port=env.Postgres.PORT,
    user=read_file(env.Postgres.USER_FILE),
    password=read_file(env.Postgres.PASSWORD_FILE),
    db=read_file(env.Postgres.DB_FILE)
))

bot = SimpleLongPollBot(
    [read_file(env.Bot.ACCESS_TOKEN_FILE)],
    int(read_file(env.Bot.GROUP_ID_FILE)),
)
bot.router.registrar.add_default_filter(filters.EventTypeFilter("message_new"))

bot.dispatcher.add_router(registration.router)
bot.dispatcher.add_router(home.router)

try:
    bot.run_forever(ignore_errors=True)
except KeyboardInterrupt:
    sys.exit()
