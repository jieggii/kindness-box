from vkwave.bots import ButtonColor, Keyboard


class BoolKeyboard(Keyboard):
    TRUE: str = "True"
    FALSE: str = "False"

    def __init__(self, primary_option: bool):
        super(BoolKeyboard, self).__init__()
        true_color = ButtonColor.PRIMARY if primary_option else ButtonColor.SECONDARY
        false_color = ButtonColor.PRIMARY if not primary_option else ButtonColor.SECONDARY
        self.add_text_button(text=self.TRUE, color=true_color)
        self.add_text_button(text=self.FALSE, color=false_color)
