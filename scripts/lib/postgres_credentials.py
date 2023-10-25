from os import path

from bot.util import read_file

SECRETS_DIR = "./.secrets/postgres"  # directory where postgres credentials are stored

_POSTGRES_SECRETS_PATHS = {
    "user": path.join(SECRETS_DIR, "user"),
    "password": path.join(SECRETS_DIR, "password"),
    "db": path.join(SECRETS_DIR, "db"),
}


def read_postgres_credentials() -> (str, str, str):
    """Reads credentials from secrets directory. Returns user, password and db name."""
    return (
        read_file(_POSTGRES_SECRETS_PATHS["user"]),
        read_file(_POSTGRES_SECRETS_PATHS["password"]),
        read_file(_POSTGRES_SECRETS_PATHS["db"]),
    )
