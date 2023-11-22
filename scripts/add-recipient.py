import argparse
import asyncio
from bot.database.models import Municipality, Recipient

from bot.database.init import init_database

from loguru import logger

MONGO_USERNAME_FILE = "./.secrets/mongo/username"
MONGO_PASSWORD_FILE = "./.secrets/mongo/password"


def read_file(file_path: str) -> str:
    with open(file_path, "r") as file:
        return file.read().strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="add-recipient.py",
        description="Use this script to manually add a new recipient to the database",
    )

    database_group = parser.add_argument_group("database connection")
    database_group.add_argument("--host", type=str, default="localhost", help="database host")
    database_group.add_argument("--port", "-p", type=int, default=27017, help="database port")
    database_group.add_argument("--database", "-d", type=str, default="kindness-box", help="database name")

    recipient_group = parser.add_argument_group("recipient information")
    recipient_group.add_argument("--name", "-n", type=str, help="recipient name", required=True)
    recipient_group.add_argument("--age", "-a", type=int, help="recipient age", required=True)
    recipient_group.add_argument("--id", "-i", type=int, help="recipient identifier", required=True)
    recipient_group.add_argument("--gift", "-g", type=str, help="recipient gift description", required=True)

    return parser.parse_args()


def main():
    args = parse_args()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    logger.info("reading mongo credentials")
    username, password = read_file(MONGO_USERNAME_FILE), read_file(MONGO_PASSWORD_FILE)

    logger.info(f"connecting to mongo database {args.database} at {username}@{args.host}:{args.port}")

    loop.run_until_complete(
        init_database(host=args.host, port=args.port, username=username, password=password, database=args.database)
    )

    municipalities = loop.run_until_complete(Municipality.find_all().to_list())
    print("Available municipalities:")
    for i, municipality in enumerate(municipalities):
        print(f"{i + 1}. {municipality.name}")

    municipality_number = int(input("choose municipality > "))
    recipient = Recipient(
        identifier=args.id,
        name=args.name,
        age=args.age,
        gift_description=args.gift,
        municipality=municipalities[municipality_number - 1]
    )
    result = loop.run_until_complete(recipient.save())
    print(result)


if __name__ == '__main__':
    main()
