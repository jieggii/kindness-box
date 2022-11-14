import asyncio
from logging import basicConfig, getLogger
from os import getenv
from typing import List

from udpy import AsyncUrbanClient, UrbanDefinition

from vkwave.api import API, BotSyncSingleToken
from vkwave.bots import (
    Dispatcher,
    EventTypeFilter,
    TextFilter,
    BotEvent,
    BotLongpollExtension,
    DefaultRouter,
    TokenStorage,
    GroupId,
)
from vkwave.client import AIOHTTPClient
from vkwave.longpoll import BotLongpoll, BotLongpollData

basicConfig(level="DEBUG")
logger = getLogger(__name__)

text = lambda text: TextFilter(text)
text_startswith = lambda text: lambda event: event.object.object.message.text.startswith(text)
new_message = EventTypeFilter("message_new")

router = DefaultRouter()
wd = router.registrar.with_decorator
api = API(BotSyncSingleToken(getenv("TOKEN")), AIOHTTPClient())
token_storage = TokenStorage[GroupId]()

dp = Dispatcher(api, token_storage)
ext = BotLongpollExtension(dp, BotLongpoll(api.get_context(), BotLongpollData(getenv("GROUP_ID"))))

client = AsyncUrbanClient()


def make_result(defs: List[UrbanDefinition]) -> str:
    result = ""

    for i, d in enumerate(defs, start=1):
        if i == 4:
            break
        result += f"{d.word}: {d.definition}\nExample: \n{d.example}"

    return result


@wd(new_message, text("random"))
async def handle_random(event: BotEvent) -> str:
    random_defs = await client.get_random_definition()
    return make_result(random_defs)


@wd(new_message, text_startswith("meaning"))
async def handle_meaning(event: BotEvent) -> str:
    defs = await client.get_definition(" ".join(event.object.object.message.text.split()[1:]))
    return make_result(defs)


dp.add_router(router)


async def main():
    await dp.cache_potential_tokens()
    await ext.start()
    logger.debug("Bot started!")


loop = asyncio.get_event_loop()
loop.create_task(main())
loop.run_forever()
