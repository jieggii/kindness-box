from vkwave.bots import ButtonColor, Keyboard


class ChooseMunicipalityKeyboard(Keyboard):
    def __init__(self, municipality_names: list[str]):
        super(ChooseMunicipalityKeyboard, self).__init__()

        for i, name in enumerate(municipality_names):
            self.add_text_button(text=name, color=ButtonColor.SECONDARY)
            if (i + 1) % 2 == 0 and i < len(municipality_names) - 1:
                self.add_row()


class ChooseOrganizationOptionKeyboard(Keyboard):
    BY_MYSELF = "От своего"
    BY_ORGANIZATION = "От имени организации"

    def __init__(self):
        super(ChooseOrganizationOptionKeyboard, self).__init__()
        self.add_text_button(text=self.BY_MYSELF, color=ButtonColor.PRIMARY)
        self.add_text_button(text=self.BY_ORGANIZATION, color=ButtonColor.SECONDARY)
