import re
import unicodedata


LEGAL = {"limited", "ltd", "llc", "inc", "incorporated", "corp", "corporation", "company", "co", "private", "pvt", "plc"}


def normalize(value):
    text = unicodedata.normalize("NFKD", str(value or "")).encode("ascii", "ignore").decode().lower()
    text = text.replace("&", " and ")
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def compact(value):
    return normalize(value).replace(" ", "")


def tokens(value):
    return [token for token in normalize(value).split() if len(token) >= 2]


def useful_tokens(value):
    return sorted(set(token for token in tokens(value) if token not in LEGAL and len(token) >= 3))


def numbers(value):
    return sorted(set(re.findall(r"\d+", str(value or ""))))


def row_views(row):
    return {
        "name": normalize(row.get("business_name", "")),
        "name_compact": compact(row.get("business_name", "")),
        "name_tokens": useful_tokens(row.get("business_name", "")),
        "address": normalize(row.get("business_address", "")),
        "address_compact": compact(row.get("business_address", "")),
        "address_tokens": useful_tokens(row.get("business_address", "")),
        "numbers": numbers(row.get("business_address", "")),
        "country": str(row.get("country", "")),
    }