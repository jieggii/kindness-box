import re
from typing import List

_MOBILE_PHONE_PATTERN = r"^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$"
_LIST_OF_CHILD_IDS_PATTERN = r"\d+"


def get_list_of_child_ids(text: str) -> List[int]:
    return [int(x) for x in re.findall(_LIST_OF_CHILD_IDS_PATTERN, text)]


def is_phone_number(text: str) -> bool:
    return bool(re.fullmatch(_MOBILE_PHONE_PATTERN, text))
