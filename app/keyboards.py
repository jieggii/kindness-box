from vkwave.bots import ButtonColor, Keyboard

from app.db.models import PointCity


class CancelKeyboard(Keyboard):
    CANCEL = "Отмена"

    def __init__(self):
        super(CancelKeyboard, self).__init__()
        self.add_text_button(text=self.CANCEL, color=ButtonColor.SECONDARY)


class HomeNoChildrenKeyboard(Keyboard):
    EDIT_MY_LIST = "Выбрать детей"
    REJECT_PARTICIPATION = "Отказаться от участия"

    def __init__(self):
        super(HomeNoChildrenKeyboard, self).__init__()
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


class YesNoKeyboard(Keyboard):
    YES = "Да"
    NO = "Нет"

    def __init__(self):
        super(YesNoKeyboard, self).__init__()
        self.add_text_button(text=self.YES, color=ButtonColor.PRIMARY)
        self.add_text_button(text=self.NO, color=ButtonColor.SECONDARY)


class ChooseCityKeyboard(Keyboard):
    def __init__(self):
        super(ChooseCityKeyboard, self).__init__()
        for i, city in enumerate(PointCity):
            self.add_text_button(text=city, color=ButtonColor.SECONDARY)
            if (i + 1) % 2 == 0:
                self.add_row()


class OrgOrSelfChoiceKeyboard(Keyboard):
    SELF = "От своего"
    ORG = "От имени организации"

    def __init__(self):
        super(OrgOrSelfChoiceKeyboard, self).__init__()
        self.add_text_button(text=self.SELF, color=ButtonColor.PRIMARY)
        self.add_text_button(text=self.ORG, color=ButtonColor.SECONDARY)
