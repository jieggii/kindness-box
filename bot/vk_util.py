import typing

from vkwave.bots import SimpleBotEvent


async def fetch_current_user_name(event: SimpleBotEvent) -> (str, str):
    """Returns first name and last name of a user initiated the event.

    Parameters
    ----------
    event : SimpleBotEvent
        VK event.

    Returns
    ------
    (str, str)
        First name and last name.
    """
    data = (await event.api_ctx.users.get(user_ids=event.from_id)).response[0]
    print(data)
    return data.first_name, data.last_name


def batch_message(message: str, batch_size: int = 17) -> typing.Generator[str, None, None]:
    """Splits message into batches.

    Message batching is needed due to VK message length limit.

    Parameters
    ----------
    message : str
        Message you want to be split in batches.
    batch_size : int
        Size of one batch (lines count).
    """
    lines = message.split("\n")
    for i in range(0, len(lines), batch_size):
        yield "\n".join(lines[i : batch_size + i])
