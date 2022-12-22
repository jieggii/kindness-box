import logging

from vkwave.bots import BotEvent, DefaultRouter, Keyboard, SimpleBotEvent
from vkwave.bots.fsm import NO_STATE, ForWhat, StateFilter

from app import aliases, api_util, db, templates, user_input
from app.db.models import Donator, Point, PointLocality
from app.fsm import FSM, HomeState, RegistrationState
from app.keyboards import ChooseCityKeyboard, OrgOrSelfChoiceKeyboard
from app.routers import home

logger = logging.getLogger(__name__)

FOR_USER = ForWhat.FOR_USER

router = DefaultRouter()
reg = router.registrar


@reg.with_decorator(StateFilter(fsm=FSM, state=NO_STATE, for_what=FOR_USER))
async def no_state(event: BotEvent):
    event = SimpleBotEvent(event)
    user_id = event.from_id

    donator = await db.util.get_donator(user_id)
    if not donator:
        logger.info(f"New user (vk.com/id{user_id}) started registration")
        user_data = await api_util.get_user_data(event)
        name = user_data.first_name

        await event.answer(
            f"Привет, {name}! Я Щедрый Бот -- бот для акции <<Щедрый Вторник>>.\n\n"
            "С моей помощью ты сможешь выбрать одного или нескольких человек с "
            "ограниченными возможностями, которым будешь дарить подарок 🎅🏻\n\n"
            f"Внимание! Выбранные подарки будет необходимо принести до {templates.DEADLINE}.\n"
            "Но, для начала, мне нужно узнать некоторую информацию о тебе."
        )
        await choose_city(event)
    else:
        logger.warning(f"Got existing donator without state ({donator}), sending him home")
        await home.send_home(event)


async def choose_city(event: BotEvent):
    event = SimpleBotEvent(event)
    kbd = ChooseCityKeyboard()
    await event.answer(
        "Выбери населенный пункт, в котором ты будешь принимать участие в акции:",
        keyboard=kbd.get_keyboard(),
    )
    await FSM.set_state(state=RegistrationState.SET_LOCALITY, event=event, for_what=FOR_USER)


@reg.with_decorator(StateFilter(fsm=FSM, state=RegistrationState.SET_LOCALITY, for_what=FOR_USER))
async def set_city(event: BotEvent):
    event = SimpleBotEvent(event)
    locality = event.text
    if locality in iter(PointLocality):
        kbd = OrgOrSelfChoiceKeyboard()
        await event.answer(
            "Ты будешь участвовать в акции от своего имени, или от имени организации?",
            keyboard=kbd.get_keyboard(),
        )
        await FSM.add_data(event, for_what=FOR_USER, state_data={"point_locality": locality})
        await FSM.set_state(
            state=RegistrationState.CHOOSE_SELF_OR_ORG, event=event, for_what=FOR_USER
        )
    else:
        await event.answer(
            "Этот город не участвует в акции! Пожалуйста, выбери название города с помощью клавиатуры."
        )


@reg.with_decorator(
    StateFilter(fsm=FSM, state=RegistrationState.CHOOSE_SELF_OR_ORG, for_what=FOR_USER)
)
async def choose_self_or_org(event: BotEvent):
    event = SimpleBotEvent(event)
    text = event.text
    if text == OrgOrSelfChoiceKeyboard.SELF:
        await request_phone_number(event)
        await FSM.set_state(
            state=RegistrationState.SET_PHONE_NUMBER, event=event, for_what=FOR_USER
        )
        await FSM.add_data(event=event, for_what=FOR_USER, state_data={"org_name": None})
    elif text == OrgOrSelfChoiceKeyboard.ORG:
        kbd = Keyboard()
        await event.answer(
            "Хорошо. Тогда напиши, пожалуйста, название этой организации.",
            keyboard=kbd.get_empty_keyboard(),
        )
        await FSM.set_state(state=RegistrationState.SET_ORG_NAME, event=event, for_what=FOR_USER)
    else:
        await event.answer(templates.INVALID_OPTION)


@reg.with_decorator(StateFilter(fsm=FSM, state=RegistrationState.SET_ORG_NAME, for_what=FOR_USER))
async def set_org_name(event: BotEvent):
    event = SimpleBotEvent(event)
    org_name = event.text
    if len(org_name) > 500:
        return await event.answer(f"Слишком длинное название организации. {templates.TRY_AGAIN}")

    await request_phone_number(event)
    await FSM.set_state(state=RegistrationState.SET_PHONE_NUMBER, event=event, for_what=FOR_USER)
    await FSM.add_data(event=event, for_what=FOR_USER, state_data={"org_name": org_name})


async def request_phone_number(event: BotEvent):
    event = SimpleBotEvent(event)
    kbd = Keyboard()
    await event.answer(
        "Отлично! Теперь, пожалуйста, отправь номер телефона по которому, "
        "в случае чего, волонтеры смогли бы с тобой связаться.",
        keyboard=kbd.get_empty_keyboard(),
    )


@reg.with_decorator(
    StateFilter(fsm=FSM, state=RegistrationState.SET_PHONE_NUMBER, for_what=FOR_USER)
)
async def set_phone_number(event: BotEvent):
    event = SimpleBotEvent(event)
    phone_number = event.text

    if user_input.is_phone_number(phone_number):
        if phone_number == "88005553535":
            await event.answer("Эй, что за приколы?) Давай нормальный номер!")
            return
        await FSM.add_data(
            event=event, for_what=FOR_USER, state_data={"phone_number": phone_number}
        )
        await request_registration_confirmation(event)
    else:
        await event.answer(
            f"Эээ... Это что-то не очень похоже на номер телефона. {templates.TRY_AGAIN}"
        )


async def request_registration_confirmation(event: BotEvent):
    event = SimpleBotEvent(event)
    fsm_data = await FSM.get_data(event=event, for_what=FOR_USER)

    point_locality = fsm_data["point_locality"]
    org_name = fsm_data["org_name"]
    phone_number = fsm_data["phone_number"]

    response = "Давай проверим данные:\n"
    response += f"Населенный пункт: {point_locality}\n"
    if org_name:
        response += f"Организация: <<{org_name}>>\n"
    else:
        response += "Участвуешь в акции не от имени организации\n"
    response += f"Контактный номер телефона: {phone_number}\n"
    response += "\nВсе верно?"

    await aliases.send_confirmation(
        event=event,
        text=response,
        confirmation_handler_state=RegistrationState.CONFIRM_REGISTRATION,
    )


@reg.with_decorator(
    StateFilter(fsm=FSM, state=RegistrationState.CONFIRM_REGISTRATION, for_what=FOR_USER)
)
async def confirm_registration(event: BotEvent):
    event = SimpleBotEvent(event)
    confirmation = await aliases.handle_confirmation(event)

    if confirmation is True:
        fsm_data = await FSM.get_data(event=event, for_what=FOR_USER)
        point_locality = PointLocality(fsm_data["point_locality"])
        org_name = fsm_data["org_name"]
        phone_number = fsm_data["phone_number"]

        user_data = await api_util.get_user_data(event)
        name = f"{user_data.first_name} {user_data.last_name}"
        user_id = event.from_id

        point = await Point.filter(locality=point_locality).first()
        donator = await Donator.create(
            name=name,
            vk_user_id=user_id,
            org_name=org_name,
            phone_number=phone_number,
            point=point,
        )
        await donator.save()
        logger.info(
            f"Registered new donator: {name} (vk.com/{user_id}), {point_locality}. ID: {donator.donator_id}"
        )
        await event.answer("Чудесно! Регистрация на акцию пройдена успешно.")
        await home.send_home(event)
        await FSM.set_state(state=HomeState.HOME, event=event, for_what=FOR_USER)

    elif confirmation is False:
        await event.answer("Что-ж, давай попробуем сначала. Будь внимательней в этот раз!)")
        await FSM.add_data(event=event, for_what=FOR_USER, state_data={"org_name": None})
        await choose_city(event)
