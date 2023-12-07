import argparse


def get_argument_parser(name: str, description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog=name, description=description)

    group = parser.add_argument_group("database connection")
    group.add_argument("--host", type=str, default="localhost", help="database host")
    group.add_argument("--port", "-p", type=int, default=27017, help="database port")
    group.add_argument("--database", "-d", type=str, default="kindness-box", help="database name")

    return parser
