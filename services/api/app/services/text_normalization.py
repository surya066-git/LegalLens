import re


def normalize_search_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().casefold()

