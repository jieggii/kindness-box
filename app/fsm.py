from vkwave.bots.fsm import FiniteStateMachine, State


class RegistrationState:
    SET_CITY = State("SET_CITY")

    CHOOSE_SELF_OR_ORG = State("CHOOSE_SELF_OR_ORG")
    SET_ORG_NAME = State("SET_ORG_NAME")
    CONFIRM_ORG_NAME = State("CONFIRM_ORG_NAME")

    SET_PHONE_NUMBER = State("SET_PHONE_NUMBER")
    CONFIRM_PHONE_NUMBER = State("CONFIRM_PHONE_NUMBER")

    CONFIRM_REGISTRATION = State("CONFIRM_REGISTRATION")


class HomeState:
    HOME = State("HOME")

    CONFIRM_REJECTION = State("CONFIRM_REJECTION")
    CHOOSE_CHILDREN = State("CHOOSE_CHILDREN")

    CONFIRM_I_BROUGHT_GIFTS = State("CONFIRM_I_BROUGHT_GIFTS")

    FINISH = State("FINISH")


FSM = FiniteStateMachine()
