import asyncio
import logging
import sys

import uvloop
from vkwave.bots import SimpleLongPollBot
from vkwave.bots.core.dispatching import filters

from app import db
from app.config import config
from app.routers import home, registration

logging.basicConfig(level=logging.INFO)

uvloop.install()

loop = asyncio.get_event_loop()  # todo: .new_event_loop()?
loop.run_until_complete(db.init())

bot = SimpleLongPollBot(config.TOKENS, config.GROUP_ID)
bot.router.registrar.add_default_filter(filters.EventTypeFilter("message_new"))

bot.dispatcher.add_router(registration.router)
bot.dispatcher.add_router(home.router)

try:
    bot.run_forever(ignore_errors=True)
except KeyboardInterrupt:
    sys.exit()
