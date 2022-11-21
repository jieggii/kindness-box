from app.db.models import Donator, Person
from app.keyboards import HomeKeyboard
from app.person_id import prettify_person_id

_CHECKBOX_CHECKED = "[ X ]"
_CHECKBOX_UNCHECKED = "[&#8195;]"
_nl = "\n"


def pretty_person_name(name: str):
    first_name, last_name = name.split()
    return f"{first_name} {last_name[0]}."


async def get_persons_list(current_donator: Donator) -> list[str]:
    # returns list of batches 'cause of VK message length limits.
    # one batch = one message
    batches = []
    point = await current_donator.point.first()
    persons = await Person.filter(point=point).order_by("person_id")

    current_message = ""

    for i, person in enumerate(persons):
        donator = await person.donator
        if donator:
            current_message += f"{_CHECKBOX_CHECKED} "
        else:
            current_message += f"{_CHECKBOX_UNCHECKED} "
        current_message += f"#{prettify_person_id(person.person_id)} {pretty_person_name(person.name)} {person.age} лет "

        if donator:
            if donator == current_donator:
                current_message += "(подарок уже покупаешь ты) "
            else:
                current_message += f"(подарок уже покупает @id{donator.vk_user_id}({donator.name})) "

        current_message += f"-- {person.gift}\n\n"
        if (i+1) % 17 == 0:  # todo: change batch size
            batches.append(current_message)
            current_message = ""

    if current_message:
        batches.append(current_message)

    return batches


async def get_necessary_data_list():
    return (
        "- Имя человека, для которого предназначен подарок\n"
        "- Его идентификационный номер в системе*\n"
        f"Эту информацию можно узнать, нажав на кнопку <<{HomeKeyboard.MY_LIST}>>\n\n"
        f"*Идентификационный номер -- число, написанное в скобках после символа <<#>>."
    )
