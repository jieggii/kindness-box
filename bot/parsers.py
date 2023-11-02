import re

_MOBILE_PHONE_PATTERN = r"^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$"
_RECIPIENT_IDS_PATTERN = r"\d+"


class ParsingError(Exception):
    pass


def parse_phone_number(string: str) -> str:
    """Parses phone number from string.

    Returns
    ------
    str
        Found phone number.

    Raises
    ------
    ParsingError
        If no phone number was found in the string.
    """
    if not re.fullmatch(_MOBILE_PHONE_PATTERN, string):
        raise ParsingError()
    return string


def parse_recipient_identifiers(string: str) -> list[int]:
    """Parses recipient identifiers from string.

    Returns
    ------
    list[int]
        Found recipient identifiers.

    Raises
    ------
    ParsingError
        If no recipient identifiers were found in the string.
    """
    identifiers = [int(token) for token in re.findall(_RECIPIENT_IDS_PATTERN, string)]
    if len(identifiers) == 0:
        raise ParsingError()
    return identifiers
