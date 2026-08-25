from typing import Any


SENSITIVE_KEYS = {
    "email",
    "customer_email",

    "address",
    "shipping_address",
    "billing_address",

    "risk_score",
    "fraud_score",

    "internal",
    "internal_note",
    "internal_notes",

    "warehouse_note",
    "warehouse_notes",

    "support_tags",

    "api_key",
    "openai_api_key",
    "token",
    "secret",
    "password",
}


def is_sensitive_key(
    key: str,
) -> bool:
    """
    Determine whether a dictionary key contains
    sensitive/internal data.
    """

    normalized = (
        str(key)
        .strip()
        .lower()
    )

    if normalized in SENSITIVE_KEYS:
        return True


    dangerous_fragments = (
    "email",
    "address",
    "risk_score",
    "fraud_score",
    "internal_note",
    "warehouse_note",
    "support_tag",
    "api_key",
    "password",
    "secret",
)


    return any(
    fragment
    in normalized
    for fragment
    in dangerous_fragments
)


def sanitize_value(
    value: Any,
) -> Any:
    """
    Recursively sanitize dictionaries/lists before
    writing them to logs.

    This is defense-in-depth. The order tool already
    returns a sanitized result, but logs should not rely
    exclusively on that guarantee.
    """

    if isinstance(
        value,
        dict,
    ):

        sanitized = {}

        for key, item in value.items():

            if is_sensitive_key(
                str(key)
            ):
                continue

            sanitized[
                str(key)
            ] = sanitize_value(
                item
            )

        return sanitized

    if isinstance(
        value,
        list,
    ):

        return [
            sanitize_value(
                item
            )
            for item
            in value
        ]

    if isinstance(
        value,
        tuple,
    ):

        return [
            sanitize_value(
                item
            )
            for item
            in value
        ]

    # Basic JSON-safe primitive types.
    if value is None:
        return None

    if isinstance(
        value,
        (
            str,
            int,
            float,
            bool,
        ),
    ):
        return value

    # Fall back to string representation for objects
    # such as dates.
    return str(
        value
    )