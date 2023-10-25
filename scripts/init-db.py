"""
    init-db.py is a script for initializing kindness-box database.
    It requires installation of the project via pdm with dev dependencies.
    Must be run only from the project home directory.
    pdm run python scripts/init-db.py persons.xlsx

    notes:
    - run on totally empty db right after user creation
    - count of person numbers in the XLSX document must be bigger than count of persons
    - check if locality names are correct in the XLSX document before running this script
"""

import argparse
import asyncio
import sys

import postgres_credentials
from bot import db
from openpyxl import load_workbook

ADDRESSES = {
    db.models.PointLocality.PETROZAVODSK: "петрозаводск1",
    db.models.PointLocality.KOSTOMUKSHA: "костомукша1",
    db.models.PointLocality.MUEZERSKIY: "муезерский1",
    db.models.PointLocality.KALEVALA: "калевала1"
}


def parse_args():
    parser = argparse.ArgumentParser(
        prog="init-db.py",
        description="Use this script to initialize kindness-box database",
    )

    parser.add_argument("--host", type=str, default="localhost", help="PostgreSQL host")
    parser.add_argument("-p", "--port", type=int, default=5432, help="PostgreSQL port")
    parser.add_argument("file", type=argparse.FileType("rb"), help="XLSX file in special format")
    # Excel table format:
    # id | Name and lastname | Age | Locality | Gift description |
    # 0    1                   2     3          4
    return parser.parse_args()


def main():
    args = parse_args()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    print(f"[*] Reading PostgreSQL credentials from {postgres_credentials.SECRETS_DIR}")
    user, password, db_name = postgres_credentials.read_postgres_credentials()

    print(
        f"[*] Connecting to PostgreSQL at {user}@{args.host}:{args.port}/{db_name}"
    )
    loop.run_until_complete(db.init(
        host=args.host,
        port=args.port,
        user=user,
        password=password,
        db=db_name
    ))

    print("[*] Adding points to the database")

    points = {}
    for i, municipality in enumerate(db.models.PointLocality):
        point_id = i + 1
        address = ""

        try:
            address = ADDRESSES[municipality]
        except KeyError:
            print(f"[!] Warning: no address set for municipality '{municipality.value}'")

        point = db.models.Point(
            point_id=point_id, locality=municipality.value, address=address
        )
        loop.run_until_complete(point.save())
        points[municipality.value] = point
        print(f'[+] Added new point {point}')

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
            print(
                f"[!] Warning: it seems that end of the list is reached. Last person number: {int(number - 1)}."
            )
            break

        number = int(number)
        name = name.strip()
        age = int(age)
        locality = locality.strip()
        gift = gift.strip()

        if locality not in points.keys():
            print(f'[!] Fatal error: unknown locality "{locality}" (person number: {number}).')
            sys.exit(1)

        person = db.models.Person(
            person_id=number, name=name, age=age, gift=gift, point=points[locality]
        )
        loop.run_until_complete(person.save())
        print(f"[+] Added new person {name}, person_id={number}.")


if __name__ == "__main__":
    main()
