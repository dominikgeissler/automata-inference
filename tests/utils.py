def compare_dicts_with_unordered_lists(d1: dict[str, list], d2: dict[str, list]) -> bool:
    """Compares dicts with lists as values, but ignores order.

    Args:
        d1 (dict[str, list]): The first dict.
        d2 (dict[str, list]): The second dict.

    Returns:
        bool: Indicating whether they are equal, if one ignores list order.
    """
    # Order matters for lists, maybe replace with sets (cf #20)
    if d1.keys() != d2.keys():
        print(f"{d1.keys()},{d2.keys()}")
        return False
    for k in d1.keys():
        if set(d1[k]) != set(d2[k]):
            return False
    return True
