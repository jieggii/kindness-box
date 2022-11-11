from typing import Optional

from vkwave.bots import SimpleBotEvent
from vkwave.bots.fsm import ForWhat, State

from app.fsm import FSM
from app.keyboards import YesNoKeyboard
from app.templates import INVALID_OPTION


async def send_confirmation(
    event: SimpleBotEvent,
    text: str,
    confirmation_handler_state: State,
):
    kb = YesNoKeyboard()
    await event.answer(text, keyboard=kb.get_keyboard())
    await FSM.set_state(state=confirmation_handler_state, event=event, for_what=ForWhat.FOR_USER)


async def handle_confirmation(
    event: SimpleBotEvent,
) -> Optional[bool]:  # todo?: вместо этого писать проверки на yes / no прямо в коде, так будет очевиднее
    text = event.text
    if text == YesNoKeyboard.YES:
        return True
    elif text == YesNoKeyboard.NO:
        return False
    else:
        await event.answer(INVALID_OPTION)
        return None
