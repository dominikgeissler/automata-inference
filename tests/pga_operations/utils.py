def compare_dicts_with_unordered_lists(d1: dict[str, list], d2: dict[str, list]) -> bool:
    if d1.keys() != d2.keys():
        return False
    for k in d1.keys():
        if set(d1[k]) != set(d2[k]):
            return False
    return True