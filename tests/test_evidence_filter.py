from app.agent.evidence_filter import (
    filter_generation_evidence,
)


def test_superseded_policy_not_sent_to_llm():

    passages = [
        {
            "text": "30 day return policy",
            "metadata": {
                "filename":
                    "01-returns-policy-current.md",
                "status": "active",
                "audience": "customer",
            },
        },
        {
            "text": "45 day return policy",
            "metadata": {
                "filename":
                    "02-returns-policy-legacy.md",
                "status": "superseded",
                "audience": "customer",
            },
        },
    ]

    filtered = (
        filter_generation_evidence(
            passages
        )
    )

    filenames = [
        item["metadata"]["filename"]
        for item in filtered
    ]

    assert (
        "01-returns-policy-current.md"
        in filenames
    )

    assert (
        "02-returns-policy-legacy.md"
        not in filenames
    )