def strip_whitespace(value):
    """WTForms filter: remove leading/trailing spaces from text input."""
    return value.strip() if isinstance(value, str) else value
