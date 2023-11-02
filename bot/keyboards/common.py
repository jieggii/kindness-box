from bot.keyboards.base import BoolKeyboard


class YesNoKeyboard(BoolKeyboard):
    TRUE = "Да"
    FALSE = "Нет"

    # def __init__(self, primary: bool):
    #     super(YesNoKeyboard, self).__init__(primary)
