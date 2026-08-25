import re

from app.agent.state import (
    AgentState,
    RouteType,
)
from app.tools.order_lookup import (
    extract_order_id,
)


ORDER_KEYWORDS = {
    "where is my order",
    "where is order",
    "order status",
    "track my order",
    "tracking",
    "when will it arrive",
    "when will my order arrive",
    "delivery status",
    "has my order shipped",
    "where is it",
    "when is it arriving",
}


UNSUPPORTED_ACTION_PATTERNS = [
    # Cancellation
    r"\bcancel\b",
    r"\bcancellation\b",

    # Refund
    r"\brefund\b",

    # Replacement
    r"\breplace\b",
    r"\breplacement\b",

    # Warranty approval
    r"\bapprove\s+(?:my\s+)?warranty\b",
    r"\bwarranty\s+approval\b",

    # Address changes
    r"\bchange\b.*\baddress\b",
    r"\bupdate\b.*\baddress\b",
    r"\bcorrect\b.*\baddress\b",
    r"\bmodify\b.*\baddress\b",
]


def contains_any(
    text: str,
    phrases: set[str],
) -> bool:
    """
    Return True when any phrase occurs in text.
    """

    lowered = text.lower()

    return any(
        phrase in lowered
        for phrase in phrases
    )


def requests_unsupported_action(
    text: str,
) -> bool:
    """
    Detect requests for transactional actions that this
    application cannot perform.
    """

    lowered = text.lower()

    return any(
        re.search(
            pattern,
            lowered,
        )
        is not None
        for pattern in UNSUPPORTED_ACTION_PATTERNS
    )


def determine_route(
    state: AgentState,
) -> tuple[
    RouteType,
    str,
]:
    """
    Deterministically route the current request.

    Routes:
    - knowledge
    - order
    - unsupported_action
    - blocked

    Safety blocking happens before this router.
    """

    message = state.get(
        "user_message",
        "",
    )

    lowered = message.lower()

    order_id = extract_order_id(
        message
    )

    last_order_id = state.get(
        "last_order_id"
    )

    # --------------------------------------------------
    # 1. Unsupported transactional action
    # --------------------------------------------------

    if requests_unsupported_action(
        message
    ):

        return (
            "unsupported_action",
            (
                "User requested a transactional "
                "action this application cannot perform."
            ),
        )

    # --------------------------------------------------
    # 2. Explicit order ID
    #
    # If an order ID is present and this is not a
    # transactional action, treat it as an order lookup.
    # --------------------------------------------------

    if order_id is not None:

        return (
            "order",
            "A valid order ID was present.",
        )

    # --------------------------------------------------
    # 3. Direct order-status intent
    # --------------------------------------------------

    if contains_any(
        lowered,
        ORDER_KEYWORDS,
    ):

        return (
            "order",
            (
                "User requested order-status "
                "information."
            ),
        )

    # --------------------------------------------------
    # 4. Follow-up referring to previous order
    # --------------------------------------------------

    order_followups = {
        "when will it arrive",
        "where is it",
        "has it shipped",
        "what's the status",
        "what is the status",
        "when is it arriving",
        "so when will it arrive",
        "when will it get here",
    }

    if (
        last_order_id
        and contains_any(
            lowered,
            order_followups,
        )
    ):

        return (
            "order",
            (
                "Follow-up refers to the "
                "previous order."
            ),
        )

    # --------------------------------------------------
    # 5. Everything else is a KB question
    # --------------------------------------------------

    return (
        "knowledge",
        (
            "Request requires company "
            "knowledge."
        ),
    )