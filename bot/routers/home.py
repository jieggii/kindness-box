from beanie import DeleteRules
from beanie.operators import In
from loguru import logger
from vkwave.bots import BotEvent, DefaultRouter, Keyboard, SimpleBotEvent
from vkwave.bots.fsm import ForWhat, StateFilter

from bot import fmt, messages, parsers, settings, vk_util
from bot.database.models import Donor, Municipality, Recipient
from bot.fsm import FSM, HomeState
from bot.keyboards.common import YesNoKeyboard
from bot.keyboards.home import (
    CancelKeyboard,
    ConfirmIBroughtGiftsKeyboard,
    HomeKeyboard,
    NoRecipientsHomeKeyboard,
    StartKeyboard,
)

FOR_USER = ForWhat.FOR_USER

router = DefaultRouter()
reg = router.registrar


async def send_home(event: BotEvent):
    event = SimpleBotEvent(event)
    donor = await Donor.find_one(Donor.user_id == event.from_id)

    if donor.brought_gifts:
        logger.warning("message from donor who has already brought gifts, settings state to FINISH")
        await FSM.set_state(state=HomeState.FINISH, event=event, for_what=FOR_USER)
        return

    await FSM.set_state(state=HomeState.HOME, event=event, for_what=FOR_USER)

    # if the current donor has at least one recipient:
    if await Recipient.find_one(Recipient.donor != None):  # noqa
        kbd = HomeKeyboard()
        await event.answer(messages.MAIN_MENU_CHOOSE_ACTION_USING_KBD, keyboard=kbd.get_keyboard())

    else:
        kbd = NoRecipientsHomeKeyboard()
        await event.answer(
            "Теперь ты в главном меню. "
            "Ты можешь выбрать людей, которым будешь дарить подарки, "
            "либо отказаться от участия в акции, если ты вдруг передумал(а)!",
            keyboard=kbd.get_keyboard(),
        )


async def send_all_recipients_list(event: BotEvent):
    event = SimpleBotEvent(event)
    donor = await Donor.find_one(Donor.user_id == event.from_id, fetch_links=True)

    # fetch recipients from the same municipality as donor's:
    recipients = await Recipient.find(Recipient.municipality.id == donor.municipality.id, fetch_links=True).to_list()
    if not recipients:
        await event.answer(
            "Список людей, которые нуждаются в подарке в вашем населенном пункте, еще не готов. "
            "Попробуйте снова через пару дней! 🥲🥲"
        )
        return

    message = ""
    for recipient in recipients:
        if recipient.donor:  # if recipient already has a donor
            checkbox = "[ X ]"  # checked checkbox
        else:
            checkbox = "[&#8195;]"  # unchecked checkbox

        message += f"{checkbox} #{recipient.identifier} {fmt.recipient_name(recipient.name)} {recipient.age} лет "

        if recipient.donor:
            if recipient.donor.id == donor.id:  # noqa
                message += "(подарок уже покупаешь ты) "
            else:
                message += f"(подарок уже покупает @id{recipient.donor.user_id}({recipient.donor.name})) "

        message += f"-- {recipient.gift_description}\n\n"

    await FSM.set_state(state=HomeState.CHOOSE_RECIPIENTS, event=event, for_what=FOR_USER)

    for batch in vk_util.batch_message(message):
        await event.answer(batch)

    kbd = CancelKeyboard()
    await event.answer(
        "Перечисли через запятую идентификационные номера (число после символа <<#>>) "
        f"от 1 до {settings.MAX_CHOSEN_RECIPIENTS} человек, которым будешь покупать подарок"
        f"{f' от имени организации <<{donor.organization_name}>>.' if donor.organization_name else '.'}"
        "\n"
        "Например: 1, 7, 3",
        keyboard=kbd.get_keyboard(),
    )


@reg.with_decorator(StateFilter(fsm=FSM, state=HomeState.CHOOSE_RECIPIENTS, for_what=FOR_USER))
async def choose_recipients(event: BotEvent):
    event = SimpleBotEvent(event)

    if event.text == CancelKeyboard.CANCEL:
        await send_home(event)
        return

    try:
        recipient_identifiers = parsers.parse_recipient_identifiers(event.text)
    except parsers.ParsingError:
        await event.answer("Я не понимаю тебя! Перечисли номера людей через запятую.\n" "Например: 105, 107, 103")
        return

    if len(recipient_identifiers) > settings.MAX_CHOSEN_RECIPIENTS:
        await event.answer(f"Нельзя выбрать больше {settings.MAX_CHOSEN_RECIPIENTS}-и человек. {messages.TRY_AGAIN}")
        return

    # fetch chosen recipients:
    recipients = await Recipient.find(In(Recipient.identifier, recipient_identifiers), fetch_links=True).to_list()
    if len(recipients) != len(recipient_identifiers):  # if at least one recipient hasn't been found
        await event.answer(
            f"Одного или нескольких идентификаторов из выбранных тобой не существует. {messages.TRY_AGAIN}"
        )
        return

    donor = await Donor.find_one(Donor.user_id == event.from_id, fetch_links=True)

    # check if all recipients don't have any donors yet
    # and are located in the same municipality with the donor:
    for recipient in recipients:
        if recipient.donor:
            if recipient.donor.id != donor.id:
                await event.answer(
                    f"Одному или нескольким людям из выбранных тобой уже покупает подарок кто-то другой. {messages.TRY_AGAIN}"
                )
                return
        if recipient.municipality.id != donor.municipality.id:
            await event.answer(
                f"Один или несколько человек, из выбранных тобой, находятся в другом муниципалитете. {messages.TRY_AGAIN}"
            )
            return

    # remove past assignations:
    async for recipient in Recipient.find(Recipient.donor.id == donor.id, fetch_links=True):
        recipient.donor = None
        await recipient.save()

    # assign the current donor to the chosen recipients:
    for recipient in recipients:
        recipient.donor = donor
        await recipient.save()

    message = "Отлично, теперь тебе нужно купить и упаковать подарки для этих людей:\n"
    for recipient in recipients:
        message += f"- {fmt.recipient_name(recipient.name)} (#{recipient.identifier}) -- {recipient.gift_description}\n"

    message += (
        "\n"
        "Чтобы узнать подробную информацию о том куда, "
        f"когда и в каком виде приносить подарок, нажми на кнопку <<{HomeKeyboard.INFO}>>"
    )

    await event.answer(message)
    await send_home(event)


async def send_stats(event: SimpleBotEvent):
    message = "Статистика по всем муниципалитетам:\n"

    async for municipality in Municipality.find_all():
        total_recipients = 0
        chosen_recipients = 0
        satisfied_recipients = 0  # number of recipients whose gifts has been brought to a point

        async for recipient in Recipient.find(Recipient.municipality.id == municipality.id, fetch_links=True):
            if recipient.donor:
                chosen_recipients += 1
                if recipient.donor.brought_gifts:
                    satisfied_recipients += 1

            total_recipients += 1

        message += (
            f"{municipality.name}:\n"
            f"- Выбрано {chosen_recipients}/{total_recipients} человек.\n"
            f"- Принесено {satisfied_recipients}/{chosen_recipients} подарков.\n\n"
        )

    await event.answer(message)


@reg.with_decorator(StateFilter(fsm=FSM, state=HomeState.HOME, for_what=FOR_USER))
async def home(event: BotEvent):
    event = SimpleBotEvent(event)
    donor = await Donor.find_one(Donor.user_id == event.from_id, fetch_links=True)

    recipients = await Recipient.find(Recipient.donor.id == donor.id, fetch_links=True).to_list()

    if event.text.lower() == "статистика":
        await send_stats(event)
        return

    if recipients:  # if there is at least one recipient
        match event.text:
            case HomeKeyboard.EDIT_MY_LIST:
                await send_all_recipients_list(event)

            case HomeKeyboard.MY_LIST:
                message = "Список людей, которым тебе нужно купить подарки:\n"
                for recipient in recipients:
                    message += f"- {fmt.recipient_name(recipient.name)} {recipient.age} лет (#{recipient.identifier}) -- {recipient.gift_description}\n"
                await event.answer(message)

            case HomeKeyboard.INFO:
                message = f"Отнести подарки в населенном пункте {donor.municipality.name} можно по следующим адресам:\n"
                for address in donor.municipality.addresses:
                    message += f"- {address}\n"
                message += (
                    "\n"
                    "🚨 Важно:"
                    "\n"
                    f"1. Подарки следует принести до {settings.DEADLINE}."
                    f"\n"
                    "2. На подарке должны быть подписаны имя получателя и его идентификационный номер в системе."
                    "\n"
                    f"Эту информацию можно узнать, нажав на кнопку <<{HomeKeyboard.MY_LIST}>>."
                )
                await event.answer(message)

            case HomeKeyboard.I_BROUGHT_GIFTS:
                message = "Проверь еще раз, что ты принес подарки для всех получателей:\n"
                for recipient in recipients:
                    message += f"- {recipient.name} (#{recipient.identifier}) - {recipient.gift_description}\n"

                message += (
                    "\n"
                    f"⚠️ Нажимай на кнопку <<{ConfirmIBroughtGiftsKeyboard.TRUE}>> только тогда, когда точно в этом уверен(а)!"
                )
                kbd = ConfirmIBroughtGiftsKeyboard()
                await event.answer(message, keyboard=kbd.get_keyboard())
                await FSM.set_state(state=HomeState.CONFIRM_I_BROUGHT_GIFTS, event=event, for_what=ForWhat.FOR_USER)

            case HomeKeyboard.REJECT_PARTICIPATION:
                await send_rejection_confirmation(event)

            case _:
                await event.answer(messages.INVALID_OPTION)

    else:
        match event.text:
            case NoRecipientsHomeKeyboard.EDIT_MY_LIST:
                await send_all_recipients_list(event)

            case NoRecipientsHomeKeyboard.REJECT_PARTICIPATION:
                await send_rejection_confirmation(event)

            case _:
                await event.answer(messages.INVALID_OPTION)


async def send_rejection_confirmation(event: SimpleBotEvent):
    kbd = YesNoKeyboard(primary_option=False)
    await FSM.set_state(state=HomeState.CONFIRM_REJECTION, event=event, for_what=ForWhat.FOR_USER)
    await event.answer("Ты точно хочешь отказаться от участия в акции?", keyboard=kbd.get_keyboard())


@reg.with_decorator(StateFilter(fsm=FSM, state=HomeState.CONFIRM_REJECTION, for_what=FOR_USER))
async def confirm_rejection(event: BotEvent):
    event = SimpleBotEvent(event)

    match event.text:
        case YesNoKeyboard.TRUE:
            donor = await Donor.find_one(Donor.user_id == event.from_id)

            # I don't know why, but link_rule=DeleteRules.DELETE_LINKS doesn't work, so
            # removing link to the donor being deleted manually:
            recipients = Recipient.find(Recipient.donor.id == donor.id)
            async for recipient in recipients:
                recipient.donor = None
                await recipient.save()

            await donor.delete(link_rule=DeleteRules.DELETE_LINKS)

            await event.answer(
                "Хорошо! Если передумаешь -- смело пиши сюда снова",
                keyboard=StartKeyboard().get_keyboard(),
            )
            await FSM.finish(event=event, for_what=FOR_USER)

        case YesNoKeyboard.FALSE:
            await send_home(event)

        case _:
            await event.answer(messages.INVALID_OPTION)


@reg.with_decorator(StateFilter(fsm=FSM, state=HomeState.CONFIRM_I_BROUGHT_GIFTS, for_what=FOR_USER))
async def confirm_i_brought_gifts(event: BotEvent):
    event = SimpleBotEvent(event)
    match event.text:
        case ConfirmIBroughtGiftsKeyboard.TRUE:
            donor = await Donor.find_one(Donor.user_id == event.from_id)
            donor.brought_gifts = True
            await donor.save()

            kbd = Keyboard()
            await event.answer("🥳 Ура! Спасибо огромное за участие в акции <3", keyboard=kbd.get_empty_keyboard())
            await FSM.set_state(state=HomeState.FINISH, event=event, for_what=FOR_USER)

        case ConfirmIBroughtGiftsKeyboard.FALSE:
            await send_home(event)

        case _:
            await event.answer(messages.INVALID_OPTION)


@reg.with_decorator(StateFilter(fsm=FSM, state=HomeState.FINISH, for_what=FOR_USER))
async def finish(event: BotEvent):
    event = SimpleBotEvent(event)
    if event.text == "статистика":
        await send_stats(event)