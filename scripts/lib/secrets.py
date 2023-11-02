from os import path


def _read_file(file_path: str) -> str:
    with open(file_path, "r") as file:
        return file.read().strip()


def read_mongo_secrets(secrets_path: str) -> (str, str):
    return _read_file(path.join(secrets_path, "username")), _read_file(path.join(secrets_path, "password"))
