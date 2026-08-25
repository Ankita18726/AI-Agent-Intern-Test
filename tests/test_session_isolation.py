from app.agent.service import (
    SupportAgent,
)


def test_sessions_do_not_share_order_context():

    first_agent = SupportAgent(
        session_id="isolation-a"
    )

    second_agent = SupportAgent(
        session_id="isolation-b"
    )

    first_agent.ask(
        "Where is ORD-1007?"
    )

    result = second_agent.ask(
        "When will it arrive?"
    )

    assert (
        result.get(
            "tool_called"
        )
        is False
    )

    assert (
        result.get(
            "requested_order_id"
        )
        is None
    )

    assert (
        "order id"
        in result.get(
            "answer",
            ""
        ).lower()
    )