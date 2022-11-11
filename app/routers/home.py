import logging

from vkwave.bots import BotEvent, DefaultRouter, Keyboard, SimpleBotEvent
from vkwave.bots.fsm import ForWhat, StateFilter

from app import aliases, db, output, templates, user_input
from app.db.models import Donator, Person
from app.fsm import FSM, HomeState
from app.keyboards import CancelKeyboard, HomeKeyboard, HomeNoPersonsKeyboard
from app.person_id import parse_pretty_person_id, prettify_person_id

logger = logging.getLogger(__name__)

FOR_USER = ForWhat.FOR_USER

router = DefaultRouter()
reg = router.registrar


async def send_home(event: BotEvent):
    event = SimpleBotEvent(event)
    donator = await Donator.filter(user_id=event.from_id).first()

    if donator.brought_gifts:
        logger.warning("Got message from brought_gifts==True donator. Setting state FINISH")
        await FSM.set_state(state=HomeState.FINISH, event=event, for_what=FOR_USER)
        return

    await FSM.set_state(state=HomeState.HOME, event=event, for_what=FOR_USER)

    if await db.util.donator_has_persons(donator):
        kbd = HomeKeyboard()
        await event.answer(templates.MAIN_MENU_CHOOSE_ACTION_USING_KBD, keyboard=kbd.get_keyboard())
    else:
        kbd = HomeNoPersonsKeyboard()
        await event.answer(templates.MAIN_MENU_CHOOSE_ACTION_USING_KBD, keyboard=kbd.get_keyboard())


async def send_all_persons_list(event: BotEvent):
    event = SimpleBotEvent(event)
    donator = await db.util.get_donator(event.from_id)

    await FSM.set_state(state=HomeState.CHOOSE_PERSONS, event=event, for_what=FOR_USER)
    await event.answer(await output.get_persons_list(donator))

    kbd = CancelKeyboard()
    await event.answer(
        "Перечисли через запятую идентификационные номера (число после символа <<#>>) "
        "до 5 человек, которым будешь покупать подарок"
        f"{f' от имени организации <<{donator.org_name}>>.' if donator.org_name else '.'}\n"
        "Например: 3, 11, 12",
        keyboard=kbd.get_keyboard(),
    )


@reg.with_decorator(StateFilter(fsm=FSM, state=HomeState.CHOOSE_PERSONS, for_what=FOR_USER))
async def choose_persons(event: BotEvent):
    event = SimpleBotEvent(event)
    text = event.text

    if text == CancelKeyboard.CANCEL:
        await send_home(event)
        return

    pretty_person_ids = user_input.get_list_of_person_ids(text)

    if not pretty_person_ids:
        await event.answer(
            "Я не понимаю тебя! Перечисли номера людей через запятую.\n" "Например: 3, 11, 12"
        )
        return

    if len(pretty_person_ids) > 5:
        await event.answer(f"Нельзя выбрать больше 5 человек. {templates.TRY_AGAIN}")
        return

    person_ids = [parse_pretty_person_id(pretty_id) for pretty_id in pretty_person_ids]
    persons = [await Person.filter(id=person_id).first() for person_id in person_ids]

    if not all(persons):
        await event.answer(
            f"Одного или несколько человек из выбранных тобой не существует. {templates.TRY_AGAIN}"
        )
        return

    donator = await Donator.filter(user_id=event.from_id).first()

    if await db.util.at_least_one_person_has_donator(donator, persons):
        await event.answer(
            f"Одному или нескольким людям из выбранных тобой уже кто-то покупает подарок. {templates.TRY_AGAIN}"
        )
        return

    await Person.filter(donator=donator).update(donator_id=None)  # removing previous assignations
    for person in persons:  # assigning donator to new persons
        await Person.filter(id=person.person_id).update(donator=donator)

    response = "Отлично, теперь тебе нужно купить и упаковать подарки для этих людей:\n"
    for person in persons:
        response += f"- {output.pretty_person_name(person.name)} (#{prettify_person_id(person.person_id)}) -- {person.gift}\n"

    await event.answer(response)
    await event.answer(
        "Чтобы узнать подробную информацию о том, куда, "
        f"когда и в каком виде приносить подарок, нажми на кнопку <<{HomeKeyboard.INFO}>>"
    )
    await send_home(event)


@reg.with_decorator(StateFilter(fsm=FSM, state=HomeState.HOME, for_what=FOR_USER))
async def home(event: BotEvent):
    event = SimpleBotEvent(event)
    text = event.text
    donator = await db.util.get_donator(event.user_id)
    persons = await Person.filter(donator=donator)

    if persons:
        if text == HomeKeyboard.EDIT_MY_LIST:
            await send_all_persons_list(event)
        elif text == HomeKeyboard.MY_LIST:
            response = "Список людей, которым тебе нужно купить подарки:\n"
            for i, person in enumerate(persons):
                response += f"{i + 1}. {output.pretty_person_name(person.name)} (#{prettify_person_id(person.person_id)}) -- {person.gift}\n"
            await event.answer(response)
            await event.answer(
                "\nНе забудь подписать на подарке необходимые данные:\n"
                f"{await output.get_necessary_data_list()}"
            )
        elif text == HomeKeyboard.INFO:
            point = await donator.point.first()
            await event.answer(f"Отнести подарки в городе {point.city} можно {point.address}.\n\n")
            await event.answer(
                "Обрати внимание: на подарке обязательно должны быть подписаны:\n"
                f"{await output.get_necessary_data_list()}"
            )
        elif text == HomeKeyboard.I_BROUGHT_GIFTS:
            await aliases.send_confirmation(
                event,
                text="Подтверждение:",  # todo
                confirmation_handler_state=HomeState.CONFIRM_I_BROUGHT_GIFTS,
            )

        elif text == HomeKeyboard.REJECT_PARTICIPATION:
            await send_rejection_confirmation(event)
        else:
            await event.answer(templates.INVALID_OPTION)

    else:
        if text == HomeNoPersonsKeyboard.EDIT_MY_LIST:
            await send_all_persons_list(event)
        elif text == HomeNoPersonsKeyboard.REJECT_PARTICIPATION:
            await send_rejection_confirmation(event)
        else:
            await event.answer(templates.INVALID_OPTION)


async def send_rejection_confirmation(event: SimpleBotEvent):
    await aliases.send_confirmation(
        event=event,
        text="Ты точно хочешь отказаться от участия в акции?",
        confirmation_handler_state=HomeState.CONFIRM_REJECTION,
    )


@reg.with_decorator(StateFilter(fsm=FSM, state=HomeState.CONFIRM_REJECTION, for_what=FOR_USER))
async def confirm_rejection(event: BotEvent):
    event = SimpleBotEvent(event)
    confirmation = await aliases.handle_confirmation(event)
    if confirmation is True:
        donator = await Donator.filter(user_id=event.from_id).first()
        await donator.delete()

        kbd = Keyboard()
        await event.answer(
            "Хорошо! Если передумаешь -- смело пиши сюда снова :)",
            keyboard=kbd.get_empty_keyboard(),
        )
        await FSM.finish(event=event, for_what=FOR_USER)

    elif confirmation is False:
        await send_home(event)


@reg.with_decorator(
    StateFilter(fsm=FSM, state=HomeState.CONFIRM_I_BROUGHT_GIFTS, for_what=FOR_USER)
)
async def confirm_i_brought_gifts(event: BotEvent):
    event = SimpleBotEvent(event)
    confirmation = await aliases.handle_confirmation(event)
    if confirmation is True:
        kbd = Keyboard()
        await event.answer(
            "Ура! Спасибо огромное за участие в акции <3", keyboard=kbd.get_empty_keyboard()
        )
        await Donator.filter(user_id=event.from_id).update(brought_gifts=True)
        await FSM.set_state(
            state=HomeState.FINISH, event=event, for_what=FOR_USER
        )  # todo после перезапуска посмотреть

    elif confirmation is False:
        await send_home(event)
