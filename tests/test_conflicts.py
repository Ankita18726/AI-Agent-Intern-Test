from app.agent.conflicts import (
    detect_conflict,
)


def test_breeze_current_sources_conflict():

    passages = [
        {
            "text":
                (
                    "The stainless-steel body "
                    "should be hand-washed."
                ),

            "metadata": {
                "filename":
                    "11-product-care.md",

                "status":
                    "active",

                "policy_authority":
                    "official",
            },
        },
        {
            "text":
                (
                    "All components are "
                    "dishwasher safe."
                ),

            "metadata": {
                "filename":
                    (
                        "12-breeze-tumbler-"
                        "product-card.md"
                    ),

                "status":
                    "active",

                "policy_authority":
                    "official",
            },
        },
    ]

    assert (
        detect_conflict(
            passages
        )
        is True
    )


def test_legacy_policy_not_conflict():

    passages = [
        {
            "text":
                "30 calendar days",

            "metadata": {
                "filename":
                    (
                        "01-returns-policy-"
                        "current.md"
                    ),

                "status":
                    "active",

                "policy_authority":
                    "official",
            },
        },
        {
            "text":
                "45 calendar days",

            "metadata": {
                "filename":
                    (
                        "02-returns-policy-"
                        "legacy.md"
                    ),

                "status":
                    "superseded",

                "policy_authority":
                    "official",
            },
        },
    ]

    assert (
        detect_conflict(
            passages
        )
        is False
    )