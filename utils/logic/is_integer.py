def is_integer(s: str) -> bool:
    # type: (str) -> bool
    """Checks if a string value is an integer."""
    try:
        int(s)
        return True
    except ValueError:
        return False
