from typing import List, Optional

from app.db.models import Person, Donator


async def assign_donator_to_persons(donator: Donator, persons: List[Person]):
    for person in persons:
        await Person.filter(id=person.person_id).update(donator=donator)


async def at_least_one_person_has_donator(current_donator: Donator, persons: List[Person]):
    for person in persons:
        donator = await person.donator
        if donator is not None and donator != current_donator:
            return True
    return False


async def get_donator(user_id: int) -> Optional[Donator]:
    return await Donator.filter(user_id=user_id).first()


async def donator_has_persons(donator: Donator) -> bool:
    if await Person.filter(donator=donator):
        return True
    else:
        return False
