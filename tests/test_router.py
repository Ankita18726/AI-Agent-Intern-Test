from app.agent.router import determine_route


def test_policy_question_routes_to_knowledge():

    route, _ = determine_route(
        {
            "user_message":
                "What is your return policy?"
        }
    )

    assert route == "knowledge"


def test_explicit_order_routes_to_order():

    route, _ = determine_route(
        {
            "user_message":
                "Where is ORD-1007?"
        }
    )

    assert route == "order"


def test_order_status_without_id_routes_order():

    route, _ = determine_route(
        {
            "user_message":
                "Where is my order?"
        }
    )

    assert route == "order"


def test_order_followup_uses_context():

    route, _ = determine_route(
        {
            "user_message":
                "When will it arrive?",
            "last_order_id":
                "ORD-1007",
        }
    )

    assert route == "order"


def test_cancel_routes_to_unsupported_action():

    route, _ = determine_route(
        {
            "user_message":
                "Cancel ORD-1007 for me."
        }
    )

    assert (
        route
        == "unsupported_action"
    )