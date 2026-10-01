from difflib import SequenceMatcher


def similarity(left, right):
    if not left or not right:
        return 0.0
    return SequenceMatcher(None, left, right, autojunk=False).ratio()


def feature_row(left, right):
    name = similarity(left["name_compact"], right["name_compact"])
    address = similarity(left["address_compact"], right["address_compact"])
    name_tokens = set(left["name_tokens"]) & set(right["name_tokens"])
    address_tokens = set(left["address_tokens"]) & set(right["address_tokens"])
    name_union = set(left["name_tokens"]) | set(right["name_tokens"])
    address_union = set(left["address_tokens"]) | set(right["address_tokens"])
    numbers_equal = bool(left["numbers"] and left["numbers"] == right["numbers"])
    numbers_overlap = bool(set(left["numbers"]) & set(right["numbers"]))
    country_equal = int(left["country"] == right["country"])
    exact_name = int(left["name_compact"] == right["name_compact"] and bool(left["name_compact"]))
    exact_address = int(left["address_compact"] == right["address_compact"] and bool(left["address_compact"]))
    return [
        name, address, similarity(left["name"], right["name"]),
        len(name_tokens) / max(1, len(name_union)), len(address_tokens) / max(1, len(address_union)),
        int(numbers_equal), int(numbers_overlap), country_equal, exact_name, exact_address,
        name * address, max(name, address), min(name, address),
    ]


def cheap_keep(left, right):
    f = feature_row(left, right)
    return bool(f[8] or f[9] or f[0] >= 0.52 or f[1] >= 0.48 or (f[3] >= 0.45 and f[4] >= 0.25))