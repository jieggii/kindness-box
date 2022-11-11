from vkwave.bots import SimpleBotEvent


async def get_user_data(event: SimpleBotEvent):
    return (await event.api_ctx.users.get(user_ids=event.from_id)).response[0]
