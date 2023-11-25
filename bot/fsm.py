from vkwave.bots.fsm import FiniteStateMachine, State


class FSMDataKey:
    DONOR_NAME = "donor_name"
    MUNICIPALITY_NAME = "municipality_name"
    ORGANIZATION_NAME = "organization_name"
    PHONE_NUMBER = "phone_number"


class RegistrationState:
    SET_MUNICIPALITY = State("SET_MUNICIPALITY")

    CHOOSE_ORGANIZATION_OPTION = State("CHOOSE_ORGANIZATION_OPTION")
    SET_ORGANIZATION_NAME = State("SET_ORGANIZATION_NAME")
    CONFIRM_ORGANIZATION_NAME = State("CONFIRM_ORGANIZATION_NAME")

    SET_PHONE_NUMBER = State("SET_PHONE_NUMBER")

    CONFIRM_REGISTRATION = State("CONFIRM_REGISTRATION")


class HomeState:
    HOME = State("HOME")

    CHOOSE_RECIPIENTS = State("CHOOSE_RECIPIENTS")

    CONFIRM_GIFTS_DELIVERY = State("CONFIRM_GIFTS_DELIVERY")
    CONFIRM_REJECTION = State("CONFIRM_REJECTION")

    FINISH = State("FINISH")


FSM = FiniteStateMachine()
