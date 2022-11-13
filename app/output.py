from app.db.models import Donator, Person
from app.keyboards import HomeKeyboard
from app.person_id import prettify_person_id

_CHECKBOX_CHECKED = "[ X ]"
_CHECKBOX_UNCHECKED = "[&#8195;]"
_nl = "\n"


def pretty_person_name(name: str):
    first_name, last_name = name.split()
    return f"{first_name} {last_name[0]}."


async def get_persons_list(current_donator: Donator):
    point = await current_donator.point.first()
    message = "Список подарков:\n"
    persons = await Person.filter(point=point).order_by("person_id")

    for person in persons:
        donator = await person.donator
        if donator:
            message += f"{_CHECKBOX_CHECKED} "
        else:
            message += f"{_CHECKBOX_UNCHECKED} "
        message += f"#{prettify_person_id(person.person_id)} {pretty_person_name(person.name)} {person.age} лет "

        if donator:
            if donator == current_donator:
                message += "(подарок уже покупаешь ты) "
            else:
                message += f"(подарок уже покупает @id{donator.vk_user_id}({donator.name})) "

        message += f"-- {person.gift}\n\n"

    return message


async def get_necessary_data_list():
    return (
        "- Имя человека, для которого предназначен подарок\n"
        "- Его идентификационный номер в системе*\n"
        f"Эту информацию можно узнать, нажав на кнопку <<{HomeKeyboard.MY_LIST}>>\n\n"
        f"*Идентификационный номер -- число, написанное в скобках после символа <<#>>."
    )
