from app.agent.router import (
    determine_route,
)


def test_shipping_address_change_routes_to_action_safety():

    route, _ = determine_route(
        {
            "user_message": (
                "Change the shipping address "
                "on ORD-1007 for me."
            )
        }
    )

    assert (
        route
        == "unsupported_action"
    )
def test_update_delivery_address_routes_to_action_safety():

    route, _ = determine_route(
        {
            "user_message": (
                "Please update the delivery "
                "address on my order."
            )
        }
    )

    assert (
        route
        == "unsupported_action"
    )
from app.agent.service import (
    SupportAgent,
)


def test_shipped_order_answer_contains_carrier():

    agent = SupportAgent(
        session_id="carrier-regression"
    )

    result = agent.ask(
        "Where is ORD-1007 "
        "and when should it arrive?"
    )

    answer = result[
        "answer"
    ]

    assert "shipped" in answer.lower()
    assert "UPS" in answer
    assert (
        "August 22, 2026"
        in answer
    )