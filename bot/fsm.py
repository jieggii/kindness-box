from vkwave.bots.fsm import FiniteStateMachine, State


class FSMDataKey:
    DONOR_NAME = "donor_name"
    MUNICIPALITY_NAME = "municipality_name"
    ORGANIZATION_NAME = "organization_name"
    PHONE_NUMBER = "phone_number"


class RegistrationState:
    SET_MUNICIPALITY = State("SET_MUNICIPALITY")

    CHOOSE_SELF_OR_ORG = State("CHOOSE_SELF_OR_ORG")
    SET_ORGANIZATION_NAME = State("SET_ORGANIZATION_NAME")
    CONFIRM_ORGANIZATION_NAME = State("CONFIRM_ORGANIZATION_NAME")

    SET_PHONE_NUMBER = State("SET_PHONE_NUMBER")
    CONFIRM_PHONE_NUMBER = State("CONFIRM_PHONE_NUMBER")

    CONFIRM_REGISTRATION = State("CONFIRM_REGISTRATION")


class HomeState:
    HOME = State("HOME")

    CONFIRM_REJECTION = State("CONFIRM_REJECTION")
    CHOOSE_PERSONS = State("CHOOSE_PERSONS")

    CONFIRM_I_BROUGHT_GIFTS = State("CONFIRM_I_BROUGHT_GIFTS")

    FINISH = State("FINISH")


FSM = FiniteStateMachine()
