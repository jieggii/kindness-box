# from __future__ import annotations

from beanie import Document, Link


class Municipality(Document):
    name: str
    address: str

    class Settings:
        name = "municipalities"

    def __str__(self):
        return f"Municipality({self.id}, {self.name}, {self.address})"


class Donor(Document):
    user_id: int  # user id in VK
    name: str
    phone_number: str
    organization_name: str | None
    municipality: Link[Municipality]

    brought_gifts: bool = False

    class Settings:
        name = "donors"

    def __str__(self) -> str:
        return f"Donor({self.id}, {self.name}, {self.municipality}, brought_gifts={self.brought_gifts}, organization_name={self.organization_name})"


class Recipient(Document):
    identifier: int
    name: str  # first name and last name divided with a space
    age: int
    gift_description: str
    municipality: Link[Municipality]  # municipality where recipient is registered

    donor: Link[Donor] | None  # donor who has bought / is going to buy a gift

    class Settings:
        name = "recipients"

    def __str__(self) -> str:
        return f"Recipient({self.id}, {self.name}, {self.donor}, identifier={self.identifier})"
