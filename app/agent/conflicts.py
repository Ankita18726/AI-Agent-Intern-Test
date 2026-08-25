from typing import Any


def normalize(
    value: Any,
) -> str:

    return str(
        value or ""
    ).strip().lower()


def is_current_official(
    passage: dict[str, Any],
) -> bool:

    metadata = passage.get(
        "metadata",
        {},
    )

    return (
        normalize(
            metadata.get(
                "status"
            )
        )
        == "active"
        and normalize(
            metadata.get(
                "policy_authority"
            )
        )
        == "official"
    )


def detect_conflict(
    passages: list[
        dict[str, Any]
    ],
) -> bool:
    """
    Detect known contradictory claims only across
    current official sources.

    A superseded document can never create a
    current conflict.
    """

    current = [
        passage
        for passage
        in passages
        if is_current_official(
            passage
        )
    ]

    filenames = {
        passage.get(
            "metadata",
            {},
        ).get(
            "filename"
        )
        for passage
        in current
    }

    filenames.discard(
        None
    )

    if len(filenames) < 2:
        return False

    combined = "\n".join(
        passage.get(
            "text",
            ""
        ).lower()
        for passage
        in current
    )

    # Deliberate corpus conflict:
    # Breeze Tumbler care guide vs product card.

    has_handwash_body = (
        "stainless-steel body"
        in combined
        and (
            "hand-washed"
            in combined
            or "hand washed"
            in combined
        )
    )

    has_all_dishwasher_safe = (
        "all components are dishwasher safe"
        in combined
    )

    if (
        has_handwash_body
        and has_all_dishwasher_safe
    ):
        return True

    return False