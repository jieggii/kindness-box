import argparse
import asyncio
import csv
from os import path

from loguru import logger

from bot.database.models import Municipality, Recipient

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


NOT_AVAILABLE = "Н/Д"


def main():
    args = parse_args()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    database.init_database(loop, args.host, args.port, args.database)

    municipalities = loop.run_until_complete(Municipality.find_all().to_list())
    for municipality in municipalities:
        filename = f"{municipality.name.lower().strip()}.csv"
        filepath = path.join(args.workdir, filename)

        with open(filepath, "w") as file:
            writer = csv.writer(file)
            writer.writerow([
                "Идентификатор получателя",
                "Имя получателя",
                "Описание подарка",
                "Статус подарка",
                "Имя донора",
                "Контакт донора",
            ])
            recipients = loop.run_until_complete(
                Recipient.find(Recipient.municipality.id == municipality.id, fetch_links=True).to_list(),
            )

            for recipient in recipients:
                donor = recipient.donor
                gift_status: str
                if donor:
                    if donor.brought_gifts:
                        gift_status = "Принесен"
                    else:
                        gift_status = "Не принесен"
                else:
                    gift_status = NOT_AVAILABLE

                writer.writerow([
                    recipient.identifier,
                    recipient.name,
                    recipient.gift_description,
                    gift_status,
                    donor.name if donor else NOT_AVAILABLE,
                    f"vk.me/id{donor.user_id}, {donor.phone_number}" if donor else NOT_AVAILABLE
                ])
        logger.info(f"wrote {filepath}")


if __name__ == "__main__":
    main()
