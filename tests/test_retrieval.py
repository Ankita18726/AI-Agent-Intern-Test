from app.retrieval.ranking import (
    calculate_precedence_score,
)


def test_active_official_customer_document_scores_high():

    metadata = {
        "status": "active",
        "policy_authority": "official",
        "audience": "customer",
    }

    score = calculate_precedence_score(
        metadata
    )

    assert score > 2


def test_superseded_document_scores_lower():

    metadata = {
        "status": "superseded",
        "policy_authority": "official",
        "audience": "customer",
    }

    score = calculate_precedence_score(
        metadata
    )

    assert score < 1


def test_internal_unapproved_content_scores_low():

    metadata = {
        "status": "draft",
        "policy_authority": "none",
        "audience": "internal",
        "customer_answering": False,
    }

    score = calculate_precedence_score(
        metadata
    )

    assert score < 0