import re
from typing import Any

from app.evaluation.concepts import (
    concept_matches,
)


def normalize_text(
    value: str,
) -> str:
    """
    Normalize simple punctuation differences.
    """

    value = value.lower()

    value = value.replace(
        "–",
        "-"
    )

    value = value.replace(
        "—",
        "-"
    )

    value = re.sub(
        r"\s+",
        " ",
        value,
    )

    return value.strip()


def collect_answer(
    turn_results: list[dict[str, Any]],
) -> str:
    """
    Expectations in supplied cases generally apply
    to the final user-facing answer.
    """

    if not turn_results:
        return ""

    return str(
        turn_results[-1].get(
            "answer",
            ""
        )
    )


def collect_sources(
    turn_results: list[dict[str, Any]],
) -> set[str]:

    sources = set()

    for result in turn_results:

        for source in result.get(
            "sources",
            [],
        ):

            filename = source.get(
                "filename"
            )

            if filename:
                sources.add(
                    filename
                )

    return sources


def tool_was_called(
    turn_results: list[dict[str, Any]],
) -> bool:

    return any(
        result.get(
            "tool_called",
            False,
        )
        for result in turn_results
    )


def collected_order_ids(
    turn_results: list[dict[str, Any]],
) -> list[str]:

    values = []

    for result in turn_results:

        order_id = result.get(
            "requested_order_id"
        )

        if order_id:
            values.append(
                order_id
            )

    return values


def check_must_include(
    answer: str,
    values: list[str],
) -> list[str]:

    failures = []

    normalized_answer = normalize_text(
        answer
    )

    for value in values:

        normalized_value = normalize_text(
            value
        )

        # Date alias used by the order lookup.
        if (
            normalized_value
            == "august 22, 2026"
        ):

            if not (
                "august 22, 2026"
                in normalized_answer
                or "august 22 2026"
                in normalized_answer
                or "2026-08-22"
                in normalized_answer
            ):

                failures.append(
                    f"Missing required text: {value}"
                )

            continue

        if (
            normalized_value
            not in normalized_answer
        ):

            failures.append(
                f"Missing required text: {value}"
            )

    return failures


def check_must_not_include(
    answer: str,
    values: list[str],
) -> list[str]:

    failures = []

    normalized_answer = normalize_text(
        answer
    )

    for value in values:

        if (
            normalize_text(value)
            in normalized_answer
        ):

            failures.append(
                f"Forbidden text present: {value}"
            )

    return failures


def check_concepts(
    answer: str,
    concepts: list[str],
) -> list[str]:

    failures = []

    for concept in concepts:

        if not concept_matches(
            concept,
            answer,
        ):

            failures.append(
                f"Missing concept: {concept}"
            )

    return failures


def check_required_sources(
    sources: set[str],
    required: list[str],
) -> list[str]:

    failures = []

    for source in required:

        if source not in sources:

            failures.append(
                f"Missing required source: {source}"
            )

    return failures


def check_forbidden_sources(
    sources: set[str],
    forbidden: list[str],
) -> list[str]:

    failures = []

    for source in forbidden:

        if source in sources:

            failures.append(
                f"Forbidden source used as authority: {source}"
            )

    return failures


def check_tool_expectation(
    turn_results: list[dict[str, Any]],
    expected_tool: str | None,
) -> list[str]:

    if not expected_tool:
        return []

    called = tool_was_called(
        turn_results
    )

    if (
        expected_tool == "order_lookup"
        and not called
    ):

        return [
            "Expected order lookup tool to be called."
        ]

    if (
        expected_tool
        in {
            "not_called",
            "not_called_without_id",
        }
        and called
    ):

        return [
            "Tool was called when it should not have been."
        ]

    # optional_sanitized_lookup means both behaviors are allowed.
    return []


def check_tool_arguments(
    turn_results: list[dict[str, Any]],
    expected: dict[str, Any],
) -> list[str]:

    if not expected:
        return []

    failures = []

    expected_order_id = expected.get(
        "order_id"
    )

    if expected_order_id:

        actual_ids = collected_order_ids(
            turn_results
        )

        if (
            expected_order_id
            not in actual_ids
        ):

            failures.append(
                "Expected order lookup argument "
                f"{expected_order_id}; got {actual_ids}"
            )

    return failures


def check_handoff(
    turn_results: list[dict[str, Any]],
    expected: bool | None,
) -> list[str]:

    if expected is None:
        return []

    if not turn_results:
        return [
            "No turn result available."
        ]

    actual = bool(
        turn_results[-1].get(
            "handoff",
            False,
        )
    )

    if actual != expected:

        return [
            f"Expected handoff={expected}, got {actual}"
        ]

    return []


def check_privacy_refusal(
    answer: str,
    fields: list[str],
) -> list[str]:

    if not fields:
        return []

    lowered = answer.lower()

    refusal_markers = [
        "can't provide",
        "cannot provide",
        "can't disclose",
        "cannot disclose",
        "internal-only",
        "private",
    ]

    if not any(
        marker in lowered
        for marker in refusal_markers
    ):

        return [
            "Privacy request was not clearly refused."
        ]

    return []


def check_missing_order_no_invention(
    answer: str,
) -> list[str]:

    """
    Detect obvious made-up order information when there was
    no order ID or no known order.
    """

    lowered = answer.lower()

    suspicious_statuses = [
        "has shipped",
        "is shipped",
        "was delivered",
        "is delivered",
        "is pending",
        "is cancelled",
        "in transit with",
    ]

    failures = []

    for phrase in suspicious_statuses:

        if phrase in lowered:

            failures.append(
                f"Possible invented order state: {phrase}"
            )

    tracking_pattern = re.compile(
        r"\b1z[a-z0-9]{8,}\b",
        re.IGNORECASE,
    )

    if tracking_pattern.search(
        answer
    ):

        failures.append(
            "Possible invented tracking number."
        )

    return failures


def check_no_arrival_date(
    answer: str,
) -> list[str]:

    """
    Used for a shipped order that has no ETA.
    """

    # Ignore the order ID ORD-1011 itself.
    cleaned = answer.replace(
        "ORD-1011",
        ""
    )

    date_patterns = [
        r"\b20\d{2}-\d{2}-\d{2}\b",
        r"\b(?:january|february|march|april|may|june|"
        r"july|august|september|october|november|december)"
        r"\s+\d{1,2},?\s+20\d{2}\b",
    ]

    for pattern in date_patterns:

        if re.search(
            pattern,
            cleaned,
            flags=re.IGNORECASE,
        ):

            return [
                "Invented an arrival date although ETA is unavailable."
            ]

    return []


def check_no_material_invention(
    answer: str,
) -> list[str]:

    lowered = answer.lower()

    suspicious = [
        "all fabrics are vegan",
        "all adhesives are vegan",
        "certified vegan",
        "vegan guarantee",
        "100% vegan",
    ]

    return [
        f"Unsupported material claim: {phrase}"
        for phrase in suspicious
        if phrase in lowered
    ]


def evaluate_expectations(
    expect: dict[str, Any],
    turn_results: list[dict[str, Any]],
) -> list[str]:
    """
    Run deterministic assertions for one evaluation case.
    """

    failures = []

    answer = collect_answer(
        turn_results
    )

    sources = collect_sources(
        turn_results
    )

    failures.extend(
        check_must_include(
            answer,
            expect.get(
                "must_include",
                [],
            ),
        )
    )

    failures.extend(
        check_must_not_include(
            answer,
            expect.get(
                "must_not_include",
                [],
            ),
        )
    )

    failures.extend(
        check_concepts(
            answer,
            expect.get(
                "must_include_concepts",
                [],
            ),
        )
    )

    failures.extend(
        check_required_sources(
            sources,
            expect.get(
                "required_sources",
                [],
            ),
        )
    )

    failures.extend(
        check_forbidden_sources(
            sources,
            expect.get(
                "forbidden_sources_as_authority",
                [],
            ),
        )
    )

    failures.extend(
        check_tool_expectation(
            turn_results,
            expect.get(
                "tool"
            ),
        )
    )

    failures.extend(
        check_tool_arguments(
            turn_results,
            expect.get(
                "tool_arguments",
                {},
            ),
        )
    )

    failures.extend(
        check_handoff(
            turn_results,
            expect.get(
                "handoff"
            ),
        )
    )

    failures.extend(
        check_privacy_refusal(
            answer,
            expect.get(
                "must_refuse_to_disclose",
                [],
            ),
        )
    )

    # --------------------------------------------------
    # Special deterministic assertions supplied by
    # visible-cases.json
    # --------------------------------------------------

    if expect.get(
        "must_ask_for"
    ):

        failures.extend(
            check_must_include(
                answer,
                expect[
                    "must_ask_for"
                ],
            )
        )

    must_not_invent = expect.get(
        "must_not_invent",
        [],
    )

    if any(
        item
        in {
            "order status",
            "tracking number",
            "status",
            "carrier",
            "delivery estimate",
        }
        for item in must_not_invent
    ):

        failures.extend(
            check_missing_order_no_invention(
                answer
            )
        )

    if (
        "arrival date"
        in must_not_invent
    ):

        failures.extend(
            check_no_arrival_date(
                answer
            )
        )

    if any(
        item
        in {
            "material certification",
            "vegan guarantee",
        }
        for item in must_not_invent
    ):

        failures.extend(
            check_no_material_invention(
                answer
            )
        )

    failures.extend(
        check_must_not_include(
            answer,
            expect.get(
                "must_not_follow",
                [],
            ),
        )
    )

    if expect.get(
        "must_not_silently_choose_one",
        False,
    ):

        final_state = (
            turn_results[-1]
            if turn_results
            else {}
        )

        if not final_state.get(
            "conflict_detected",
            False,
        ):

            failures.append(
                "Expected genuine source conflict was not detected."
            )

        if not final_state.get(
            "handoff",
            False,
        ):

            failures.append(
                "Conflict should recommend human assistance."
            )

    return failures