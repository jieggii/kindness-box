from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from .models import Donor, Municipality, Recipient

__all__ = ("init_database",)


async def init_database(host: str, port: str, username: str, password: str, database: str) -> None:
    client = AsyncIOMotorClient(f"mongodb://{username}:{password}@{host}:{port}")
    await init_beanie(client[database], document_models=[Municipality, Donor, Recipient])
