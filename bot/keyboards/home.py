from vkwave.bots import ButtonColor, Keyboard

from bot.keyboards.base import BoolKeyboard


class NoRecipientsHomeKeyboard(Keyboard):
    EDIT_MY_LIST = "Выбрать людей"
    REJECT_PARTICIPATION = "Отказаться от участия"

    def __init__(self):
        super(NoRecipientsHomeKeyboard, self).__init__()
        self.add_text_button(text=self.EDIT_MY_LIST, color=ButtonColor.PRIMARY)
        self.add_row()
        self.add_text_button(text=self.REJECT_PARTICIPATION, color=ButtonColor.SECONDARY)


class HomeKeyboard(Keyboard):
    MY_LIST = "Мой список"
    INFO = "Как и куда нести подарки?"
    EDIT_MY_LIST = "Изменить мой список"
    I_BROUGHT_GIFTS = "Я отнёс подарки"
    REJECT_PARTICIPATION = "Отказаться от участия"

    def __init__(self):
        super(HomeKeyboard, self).__init__()
        self.add_text_button(text=self.MY_LIST, color=ButtonColor.PRIMARY)
        self.add_text_button(text=self.EDIT_MY_LIST, color=ButtonColor.PRIMARY)
        self.add_row()
        self.add_text_button(text=self.INFO, color=ButtonColor.SECONDARY)
        self.add_row()
        self.add_text_button(text=self.I_BROUGHT_GIFTS, color=ButtonColor.POSITIVE)
        self.add_text_button(text=self.REJECT_PARTICIPATION, color=ButtonColor.NEGATIVE)


class CancelKeyboard(Keyboard):
    CANCEL = "Отмена"

    def __init__(self):
        super(CancelKeyboard, self).__init__()
        self.add_text_button(text=self.CANCEL, color=ButtonColor.SECONDARY)


class StartKeyboard(Keyboard):
    def __init__(self):
        super(StartKeyboard, self).__init__()
        self.add_text_button(text="Начать", color=ButtonColor.PRIMARY)


class ConfirmIBroughtGiftsKeyboard(BoolKeyboard):
    TRUE = "Да, всё верно"
    FALSE = "Отмена"

    def __init__(self):
        super(ConfirmIBroughtGiftsKeyboard, self).__init__(primary_option=False)
