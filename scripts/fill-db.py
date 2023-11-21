"""
    fill-db.py is a script for filling kindness-box database with recipients.

    It requires installation of the project via pdm with dev dependencies.
    Must be run only from the project home directory.

    CSV table format:
    | id | Name and lastname | Age | Municipality | Gift description |
      1     Ivan Ivanov       18     Костомукша    Описание подарка

    Example command:
    `pdm run python scripts/fill-db.py recipients.csv`
"""

import argparse
import asyncio
import csv
import re
import sys

from loguru import logger

from bot.database.init import init_database
from bot.database.models import Municipality, Recipient

MONGO_USERNAME_FILE = "./.secrets/mongo/username"
MONGO_PASSWORD_FILE = "./.secrets/mongo/password"

# column indexes:
ID_COL = 0
NAME_COL = 1
AGE_COL = 2
MUNICIPALITY_NAME_COL = 3
GIFT_DESCRIPTION_COL = 4

# regex patterns:
ID_PATTERN = r"^\d{1,4}$"
NAME_PATTERN = r"^[А-Я].+ [А-Я].+$"
AGE_PATTERN = r"^\d{1,2}$"
MUNICIPALITY_NAME_PATTERN = r"^[А-Я].+$"

# todo: check if gift description starts with a lowercase letter and does not
# contain a dot in the end
GIFT_DESCRIPTION_PATTERN = r"^.+$"

FAILURE_EXIT_STATUS = -1


def read_file(file_path: str) -> str:
    with open(file_path, "r") as file:
        return file.read().strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="init-db.py",
        description="Use this script to fill kindness-box database",
    )

    database_group = parser.add_argument_group("database connection")
    database_group.add_argument("--host", type=str, default="localhost", help="database host")
    database_group.add_argument("-p", "--port", type=int, default=27017, help="database port")
    database_group.add_argument("-d", "--database", type=str, default="kindness-box", help="database name")

    parser_group = parser.add_argument_group("parser settings")
    parser_group.add_argument("-l", "--last-id", type=int, default=None, help="id to interrupt parsing after")
    parser_group.add_argument(
        "-a", "--add", type=int, default=0, help="a number to be added to id to create identifier"
    )
    parser_group.add_argument("file", type=argparse.FileType("r"), help="input CSV file in special format")

    return parser.parse_args()


def log_validation_error(filename: str, line_num: int, field_name: str, field_value: str, field_pattern: str) -> None:
    log_file_error(filename, line_num, f"{field_name} '{field_value}' does not match regex pattern '{field_pattern}'")


def log_file_error(filename: str, line_num: int, message: str) -> None:
    logger.error(f"{filename}:{line_num} {message}")


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

    logger.info(f"{args.file.name}: reading")

    reader = csv.reader(args.file)
    rows = list(reader)[2:]  # skipping title and example row

    municipality_names: list[str] = []
    recipients: list[dict[str, str | int | None]] = []
    logger.info(f"{args.file.name}: validating")
    validation_failed = False
    for i, row in enumerate(rows):
        line_num = i + 3

        id = row[ID_COL]  # noqa
        name = row[NAME_COL]
        age = row[AGE_COL]
        municipality_name = row[MUNICIPALITY_NAME_COL]
        gift_description = row[GIFT_DESCRIPTION_COL]

        # check fields using regular expressions:
        if not re.fullmatch(ID_PATTERN, id):
            log_validation_error(args.file.name, line_num, "id", id, ID_PATTERN)
            validation_failed = True

        if not re.fullmatch(NAME_PATTERN, name):
            log_validation_error(args.file.name, line_num, "name", name, NAME_PATTERN)
            validation_failed = True

        if re.fullmatch(MUNICIPALITY_NAME_PATTERN, municipality_name):
            if municipality_name not in municipality_names:
                municipality_names.append(municipality_name)
        else:
            log_validation_error(
                args.file.name,
                line_num,
                "municipality name",
                municipality_name,
                MUNICIPALITY_NAME_PATTERN,
            )
            validation_failed = True

        if not re.fullmatch(GIFT_DESCRIPTION_PATTERN, gift_description):
            log_validation_error(
                args.file.name,
                line_num,
                "gift description",
                gift_description,
                GIFT_DESCRIPTION_PATTERN,
            )
            validation_failed = True

        identifier = int(id) + args.add

        # check if recipient does not already exist:
        recipient_exists = loop.run_until_complete(
            Recipient.find_one(Recipient.identifier == identifier).exists()
        )
        if recipient_exists:
            log_file_error(args.file.name, line_num, f"recipient with identifier {identifier} already exists")
            validation_failed = True

        recipients.append(
            {
                "identifier": int(id) + args.add,
                "name": name,
                "age": int(age),
                "municipality_name": municipality_name,
                "gift_description": gift_description,
            }
        )

        if i + 1 == args.last_id:  # skip next rows if reached the indicated last id
            logger.warning(f"{args.file.name}:{line_num} last id is set to {args.last_id}, skipping rows after it")
            break

    logger.info(f"{args.file.name}: the following municipalities were found: {', '.join(municipality_names)}")
    if validation_failed:
        logger.info("exiting due to previous validation errors (no write operations were executed)")
        sys.exit(FAILURE_EXIT_STATUS)

    option = input("Would you like to continue? (y/n) > ")  # this is needed to avoid typos in municipality names
    if option.lower() not in ["y", "yes"]:
        logger.info("aborted")
        sys.exit()

    # save non-stored municipalities:
    for municipality_name in municipality_names:
        if not loop.run_until_complete(Municipality.find_one(Municipality.name == municipality_name)):
            logger.info(f"storing municipality '{municipality_name}' as it does not exist in the database")
            municipality = Municipality(name=municipality_name, address="")
            loop.run_until_complete(municipality.save())

    # save recipients:
    for recipient_data in recipients:
        identifier = recipient_data["identifier"]
        name = recipient_data["name"]
        age = recipient_data["age"]
        municipality_name = recipient_data["municipality_name"]
        gift_description = recipient_data["gift_description"]

        municipality = loop.run_until_complete(
            Municipality.find_one(Municipality.name == municipality_name),
        )
        if not municipality:
            logger.error(f"municipality '{municipality_name}' was not found")

        recipient = Recipient(
            identifier=identifier,
            name=name,
            age=age,
            municipality=municipality,
            gift_description=gift_description,
        )
        result = loop.run_until_complete(recipient.save())
        logger.info(f"stored a new recipient: {result}")

    logger.info("done! don't forget to set municipality addresses in the database ;)")


if __name__ == "__main__":
    main()
