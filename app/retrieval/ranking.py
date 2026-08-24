from typing import Any


STATUS_SCORES = {
    "active": 1.0,
    "superseded": -1.0,
    "draft": -0.8,
}


AUTHORITY_SCORES = {
    "official": 1.0,
    "none": -1.0,
}


AUDIENCE_SCORES = {
    "customer": 0.5,
    "internal": -0.5,
}


def calculate_precedence_score(
    metadata: dict[str, Any],
) -> float:
    """
    Calculate a deterministic precedence score.

    This does NOT replace semantic similarity.
    It is used to adjust retrieval ranking based
    on document authority.
    """

    score = 0.0

    status = metadata.get(
        "status",
        "",
    )

    authority = metadata.get(
        "policy_authority",
        "",
    )

    audience = metadata.get(
        "audience",
        "",
    )

    score += STATUS_SCORES.get(
        status,
        0.0,
    )

    score += AUTHORITY_SCORES.get(
        authority,
        0.0,
    )

    score += AUDIENCE_SCORES.get(
        audience,
        0.0,
    )

    # Explicitly unapproved customer content
    if metadata.get(
        "customer_answering"
    ) is False:

        score -= 2.0

    return score