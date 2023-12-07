import argparse
import asyncio

from loguru import logger

from bot.database.models import Municipality, Recipient

from common import argument_parser, database


def read_file(file_path: str) -> str:
    with open(file_path, "r") as file:
        return file.read().strip()


def parse_args() -> argparse.Namespace:
    parser = argument_parser.get_argument_parser(
        name="add-recipient.py",
        description="Use this script to manually add a new recipient to the database",
    )

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
    database.init_database(loop, args.host, args.port, args.database)

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
        municipality=municipalities[municipality_number - 1],
    )
    result = loop.run_until_complete(recipient.save())
    print(result)


if __name__ == "__main__":
    main()
