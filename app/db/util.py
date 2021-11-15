from typing import List, Optional

from app.db.models import Child, Donator


async def assign_donator_to_children(donator: Donator, children: List[Child]):
    for child in children:
        await Child.filter(id=child.id).update(donator=donator)


async def at_least_one_child_has_donator(current_donator: Donator, children: List[Child]):
    for child in children:
        donator = await child.donator
        if donator is not None and donator != current_donator:
            return True
    return False


async def get_donator(user_id: int) -> Optional[Donator]:
    return await Donator.filter(user_id=user_id).first()


async def donator_has_children(donator: Donator) -> bool:
    if await Child.filter(donator=donator):
        return True
    else:
        return False
