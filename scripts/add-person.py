import argparse
import asyncio


def parse_args():
    parser = argparse.ArgumentParser(
        prog="init-db.py",
        description="Use this script to initialize kindness-box database",
    )
    parser.add_argument(
        "-e", "--env", type=argparse.FileType(), default=None, help=".env file to use"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    if args.env:
        import dotenv

        dotenv.load_dotenv(stream=args.env)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    print("[*] Reading env")

    print(
        f"[*] Connecting to postgresql at {config.PG.USER}@{config.PG.HOST}:{config.PG.PORT}/{config.PG.DATABASE}"
    )
    loop.run_until_complete(db.init())

    name = input("name: ")
    age = int(input("age: "))
    gift = input("gift (first letter lowercase): ")
    point_id = int(input("point_id: "))

    point = loop.run_until_complete(asyncio.gather(db.models.Point.get(point_id=point_id)))[0]
    print(point)

    last_person = loop.run_until_complete(
        asyncio.gather(db.models.Person.all().order_by("-person_id").first())
    )[0]
    person = db.models.Person(
        person_id=last_person.person_id + 1, name=name, age=age, gift=gift, point=point
    )
    loop.run_until_complete(person.save())
    print(f"[+] Added new person to point {point.locality}.")


if __name__ == "__main__":
    main()
