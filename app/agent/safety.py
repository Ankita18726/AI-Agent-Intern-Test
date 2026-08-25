import re


# --------------------------------------------------
# Requests that should be refused at application level
# --------------------------------------------------

SECRET_REQUEST_PATTERNS = [
    r"\bsystem prompt\b",
    r"\bhidden prompt\b",
    r"\bhidden instruction",
    r"\binternal instruction",
    r"\breveal.*prompt\b",
    r"\bshow.*prompt\b",
    r"\bdeveloper message\b",
]


INTERNAL_DATA_PATTERNS = [
    r"\brisk score\b",
    r"\binternal note",
    r"\bwarehouse note",
    r"\bsupport tag",
]


def is_secret_request(
    message: str,
) -> bool:
    """
    Detect explicit requests for hidden application
    instructions or secrets.
    """

    text = message.lower()

    return any(
        re.search(pattern, text)
        for pattern in SECRET_REQUEST_PATTERNS
    )


def is_internal_data_request(
    message: str,
) -> bool:
    """
    Detect explicit requests for internal-only order data.
    """

    text = message.lower()

    return any(
        re.search(pattern, text)
        for pattern in INTERNAL_DATA_PATTERNS
    )


def get_block_reason(
    message: str,
) -> str | None:

    if is_secret_request(message):

        return "hidden_instructions"

    if is_internal_data_request(message):

        return "internal_data"

    return None