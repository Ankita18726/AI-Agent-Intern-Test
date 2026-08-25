from app.agent.service import SupportAgent
def test_agent_normalizes_lowercase_order_id():

    agent = SupportAgent(
        session_id="lowercase-agent"
    )

    result = agent.ask(
        "Check ord-1007 please."
    )

    assert (
        result[
            "tool_called"
        ]
        is True
    )

    assert (
        result[
            "requested_order_id"
        ]
        == "ORD-1007"
    )

def test_standard_return_does_not_use_legacy_source():

    agent = SupportAgent(
        session_id="return-precedence"
    )

    result = agent.ask(
        "How long does a regular customer "
        "have to return an unused backpack?"
    )

    filenames = {
        source[
            "filename"
        ]
        for source
        in result[
            "sources"
        ]
    }

    assert (
        "01-returns-policy-current.md"
        in filenames
    )

    assert (
        "02-returns-policy-legacy.md"
        not in filenames
    )

    assert (
        "14-internal-content-migration-notes.md"
        not in filenames
    )

    assert (
        result["handoff"]
        is False
    )