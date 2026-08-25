from app.agent.nodes import (
    build_retrieval_query,
)


def test_short_standalone_question_not_polluted():

    state = {
        "user_message":
            "Do you ship internationally?",

        "history": [
            {
                "role":
                    "user",

                "content":
                    (
                        "How long do I have "
                        "to return a backpack?"
                    ),
            }
        ],

        "current_topic":
            "return policy",
    }

    result = (
        build_retrieval_query(
            state
        )
    )

    assert (
        result
        == "Do you ship internationally?"
    )


def test_canada_followup_uses_history():

    state = {
        "user_message":
            "What about Canada?",

        "history": [
            {
                "role":
                    "user",

                "content":
                    "Do you ship internationally?",
            }
        ],

        "current_topic":
            "international shipping",
    }

    result = (
        build_retrieval_query(
            state
        )
    )

    assert (
        "Do you ship internationally?"
        in result
    )

    assert (
        "What about Canada?"
        in result
    )