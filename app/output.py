from app.child_id import prettify_child_id
from app.db.models import Child, Donator
from app.keyboards import HomeKeyboard

_CHECKBOX_CHECKED = "[ X ]"
_CHECKBOX_UNCHECKED = "[&#8195;]"
_nl = "\n"


def pretty_child_name(name: str):
    first_name, last_name = name.split()
    return f"{first_name} {last_name[0]}."


async def get_children_list(current_donator: Donator):
    point = await current_donator.point.first()
    message = "Список подарков:\n"
    children = await Child.filter(point=point).order_by("id")

    for child in children:
        donator = await child.donator
        if donator:
            message += f"{_CHECKBOX_CHECKED} "
        else:
            message += f"{_CHECKBOX_UNCHECKED} "
        message += f"#{prettify_child_id(child.id)} {pretty_child_name(child.name)}, {child.age} лет "

        if donator:
            if donator == current_donator:
                message += "(подарок уже покупаешь ты) "
            else:
                message += f"(подарок уже покупает @id{donator.user_id}({donator.name})) "

        message += f"-- {child.gift}\n\n"

    return message


async def get_necessary_data_list():
    return (
        "- Имя человека, для которого предназначен подарок\n"
        "- Его идентификационный номер в системе*\n"
        f"Эту информацию можно узнать, нажав на кнопку <<{HomeKeyboard.MY_LIST}>>\n"
        f"*Идентификационный номер -- число, написанное в скобках после символа <<#>>."
    )
