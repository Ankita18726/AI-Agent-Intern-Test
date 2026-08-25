from app.agent.service import SupportAgent


def test_missing_order_id_does_not_lookup():

    agent = SupportAgent(
        session_id="test-missing-id"
    )

    result = agent.ask(
        "Where is my order?"
    )

    assert (
        result["tool_called"]
        is False
    )

    assert (
        "provide" in
        result["answer"].lower()
    )


def test_order_lookup_occurs():

    agent = SupportAgent(
        session_id="test-order"
    )

    result = agent.ask(
        "Where is ORD-1007?"
    )

    assert (
        result["tool_called"]
        is True
    )

    assert (
        result["requested_order_id"]
        == "ORD-1007"
    )
def test_cancelled_order_does_not_report_eta():

    agent = SupportAgent(
        session_id="cancelled-order-test"
    )

    result = agent.ask(
        "When will ORD-1004 arrive?"
    )

    answer = result[
        "answer"
    ].lower()

    assert "cancelled" in answer
    assert "will not be shipped" in answer

    assert "estimated delivery" not in answer
    assert "delivery date" not in answer
def test_insufficient_answer_has_no_irrelevant_sources():

    agent = SupportAgent(
        session_id="vegan-test"
    )

    result = agent.ask(
        "Are all fabrics and adhesives "
        "in your bags vegan?"
    )

    assert (
        result[
            "insufficient_information"
        ]
        is True
    )

    assert (
        result["handoff"]
        is True
    )

    assert result["sources"] == []
def test_followup_preserves_order():

    agent = SupportAgent(
        session_id="test-followup"
    )

    first = agent.ask(
        "Where is ORD-1007?"
    )

    assert (
        first["last_order_id"]
        == "ORD-1007"
    )

    second = agent.ask(
        "When will it arrive?"
    )

    assert (
        second["requested_order_id"]
        == "ORD-1007"
    )

def test_breeze_conflict_requires_handoff():

    agent = SupportAgent(
        session_id="breeze-test"
    )

    result = agent.ask(
        "Can I put the entire Breeze "
        "Tumbler in the dishwasher?"
    )

    assert (
        result["conflict_detected"]
        is True
    )

    assert (
        result["handoff"]
        is True
    )

    filenames = {
        source["filename"]
        for source
        in result["sources"]
    }

    assert (
        "11-product-care.md"
        in filenames
    )

    assert (
        "12-breeze-tumbler-product-card.md"
        in filenames
    )
def test_unknown_order_does_not_invent():

    agent = SupportAgent(
        session_id="test-unknown"
    )

    result = agent.ask(
        "Where is ORD-9999?"
    )

    assert (
        result["order_result"]["found"]
        is False
    )

    assert (
        result["handoff"]
        is True
    )