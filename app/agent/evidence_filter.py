from collections import defaultdict
from typing import Any


def normalize(
    value: Any,
) -> str:
    return str(
        value or ""
    ).strip().lower()


def is_superseded(
    metadata: dict[str, Any],
) -> bool:
    return normalize(
        metadata.get(
            "status",
            "",
        )
    ) in {
        "superseded",
        "legacy",
        "deprecated",
        "inactive",
        "archived",
    }


def is_internal(
    metadata: dict[str, Any],
) -> bool:
    return (
        normalize(
            metadata.get(
                "audience",
                "",
            )
        )
        == "internal"
    )


def is_current_customer_source(
    metadata: dict[str, Any],
) -> bool:
    return (
        normalize(
            metadata.get(
                "status",
                "",
            )
        )
        == "active"
        and
        normalize(
            metadata.get(
                "audience",
                "",
            )
        )
        == "customer"
    )


def filter_generation_evidence(
    passages: list[dict[str, Any]],
    max_passages: int = 6,
) -> list[dict[str, Any]]:
    """
    Select current customer-facing evidence.

    Superseded and internal documents may be useful for
    diagnostics but should not influence the customer-facing
    answer.
    """

    safe = []

    for passage in passages:

        metadata = passage.get(
            "metadata",
            {},
        )

        if is_superseded(
            metadata
        ):
            continue

        if is_internal(
            metadata
        ):
            continue

        if not is_current_customer_source(
            metadata
        ):
            continue

        safe.append(
            passage
        )

    safe.sort(
        key=lambda item: item.get(
            "final_score",
            0,
        ),
        reverse=True,
    )

    selected = []

    per_file_count = defaultdict(
        int
    )

    for passage in safe:

        metadata = passage.get(
            "metadata",
            {},
        )

        filename = metadata.get(
            "filename",
            "unknown",
        )

        if (
            per_file_count[filename]
            >= 3
        ):
            continue

        selected.append(
            passage
        )

        per_file_count[
            filename
        ] += 1

        if (
            len(selected)
            >= max_passages
        ):
            break

    return selected