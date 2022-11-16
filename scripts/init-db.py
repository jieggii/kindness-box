# script for initializing kindness-box database
# requires installation of the project via pdm **with dev dependencies**
# must be run only from the ./scripts/ directory (relative to the project directory)

# notes:
# - run on totally empty db right after user creation
# - count of person numbers in the excel document must be bigger than count of persons
# - check if locality names are correct in the excel document before running this script

import argparse
import asyncio
import sys

from openpyxl import load_workbook


def parse_args():
    parser = argparse.ArgumentParser(
        prog="init-db.py",
        description="Use this script to initialize kindness-box database",
    )
    parser.add_argument("-x", "--exec", type=argparse.FileType(), default=None, help="SQL script to run at first")
    parser.add_argument("-e", "--env", type=argparse.FileType(), default=None, help=".env file to use")
    parser.add_argument("file", type=argparse.FileType("rb"), help="XLSX file in special format")
    # Excel table format:
    # id | Name and lastname | Age | Locality | Gift description |
    # 0    1                   2     3          4
    return parser.parse_args()


def main():
    args = parse_args()
    if args.env:
        import dotenv
        dotenv.load_dotenv(stream=args.env)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    print("[*] Reading env")
    # using async Tortoise ORM and config from the main `app` to escape from new dependencies
    # this brings some problems, e.g. GROUP_ID and other unnecessary env variables will be required too.
    # but the script is meant to be run when .env file is fulfilled, so this is not a big problem
    #
    # I think it has to bee changed in the future (#todo)
    from app import db
    from app.config import config

    print(f"[*] Connecting to {config.PG.USER}@{config.PG.HOST:{config.PG.PORT}}/{config.PG.DATABASE}")
    loop.run_until_complete(db.init())

    print("[*] Adding points to the database")
    points = {}
    for i, locality_enum in enumerate(db.models.PointLocality):
        point_id = i + 1
        point_locality = locality_enum.value
        point = db.models.Point(point_id=point_id, locality=point_locality, address=f"...")  # todo: do anything with it?
        loop.run_until_complete(point.save())
        points[point_locality] = point
        print(f'[+] Added new point "{point_locality}", point_id={point_id}.')

    print(f"[*] Reading {args.file.name}")
    wb = load_workbook(args.file)
    ws = wb.active
    rows = list(ws.rows)

    for row in rows[2:]:  # ignoring the first (title) row and the second (example) row
        number = row[0].value
        name = row[1].value
        age = row[2].value
        locality = row[3].value
        gift = row[4].value
        if not (number and name and age and locality and age):
            print(f"[!] Warning: it seems that end of the list is reached. Last person number: {int(number-1)}.")
            break

        number = int(number)
        age = int(age)

        if locality not in points.keys():
            print(f'[!] Fatal error: unknown locality "{locality}" (person number: {number}).')
            sys.exit(1)
        person = db.models.Person(person_id=number, name=name, age=age, gift=gift, point=points[locality])
        loop.run_until_complete(person.save())
        print(f"[+] Added new person {name}, person_id={number}.")


if __name__ == "__main__":
    main()