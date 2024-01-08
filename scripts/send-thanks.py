import argparse
import asyncio
import csv
import random
import time
from os import path

from loguru import logger

from bot.database.models import Municipality, Recipient, Donor
from aiohttp.client import ClientSession

from common import argument_parser, database


def read_file(file_path: str) -> str:
    with open(file_path, "r") as file:
        return file.read().strip()


def parse_args() -> argparse.Namespace:
    parser = argument_parser.get_argument_parser(
        name="create-reports.py",
        description="Use this script to create reports for all municipalities",
    )

    parser.add_argument("--workdir", "-w", type=str, default="./", help="output dir")
    return parser.parse_args()


async def send_thank(user_id: int) -> None:
    owner_id = 0
    media_id = 0

    async with ClientSession() as session:
        async with session.get(
                "https://api.vk.com/method/messages.send",
                params={
                    "user_id": user_id,
                    "access_token": "",
                    "random_id": random.randint(0, 9999999),
                    "message": 'Благодарим вас за участие в акции "Коробочка доброты"! Вы можете разместить это благодарственное письмо на своей странице, чтобы в следующем году больше людей смогли принять участие в акции.',
                    "attachment": f"photo{owner_id}_{media_id}",
                    "v": "5.199"
                },
        ) as response:
            logger.info(f'sent message: {await response.json()}')


def main():
    x = 0
    args = parse_args()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    database.init_database(loop, args.mongo_host, args.mongo_port, args.mongo_database, args.mongo_username_file,
                           args.mongo_password_file)

    donors = loop.run_until_complete(
        Donor.find_all().to_list()
    )
    for donor in donors:
        recipients = loop.run_until_complete(
            Recipient.find(Recipient.donor.id == donor.id).to_list()
        )

        if len(recipients) > 0:
            # loop.run_until_complete(send_thank(donor.user_id))
            x += 1
    print(x)


if __name__ == "__main__":
    main()
